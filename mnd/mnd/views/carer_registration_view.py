from datetime import timedelta
import uuid

from django.forms import ValidationError
from django.http.response import HttpResponseNotFound
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views import View

from registration.backends.default.views import RegistrationView

from ..forms.mnd_registration_form import MNDCarerRegistrationForm
from ..registry.patients.mnd_admin_forms import PrimaryCarerForm
from registry.patients.mixins import LoginRequiredMixin
from registry.groups.models import CustomUser

from ..models import CarerRegistration, PrimaryCarer

import logging
logger = logging.getLogger(__name__)


class PatientCarerRegistrationView(LoginRequiredMixin, View):

    def primary_carer_str(self, primary_carer):
        return f"{primary_carer.first_name} {primary_carer.last_name} ({primary_carer.email})"

    def render_form(self, request, form, primary_carer):
        return render(
            request,
            "registration/carer_enroll.html",
            context={
                "form": form,
                "carer": self.primary_carer_str(primary_carer)
            }
        )

    def has_existing_registration(self, primary_carer):
        return (
            CarerRegistration.objects.filter(
                carer=primary_carer,
                expires_on__gte=timezone.now()
            ).exists()
        )

    def get(self, request):
        if not request.user.is_patient:
            return HttpResponseNotFound()
        patient = request.user.user_object.first()
        primary_carer = PrimaryCarer.objects.filter(patient_id=patient.id).first()
        if self.has_existing_registration(primary_carer):
            form = PrimaryCarerForm(data=primary_carer.__dict__)
            form.add_error(None, ValidationError(_("A token was already generated for this carer !")))
        else:
            form = PrimaryCarerForm(instance=primary_carer)
        return self.render_form(request, form, primary_carer)

    def post(self, request):
        if not request.user.is_patient:
            return HttpResponseNotFound()
        patient = request.user.user_object.first()
        primary_carer = PrimaryCarer.objects.filter(patient_id=patient.id).first()
        if self.has_existing_registration(primary_carer):
            return HttpResponseNotFound()

        reg = CarerRegistration.objects.create(
            carer=primary_carer,
            token=uuid.uuid4(),
            expires_on=timezone.now() + timedelta(days=1)
        )
        return render(
            request,
            "registration/carer_enroll_token.html",
            context={"token": reg.token}
        )


class CarerRegistrationView(RegistrationView):

    def get(self, request, registry_code):
        request.session['REGISTRATION_CLASS'] = 'mnd.registry.groups.registration.mnd_registration.MNDCarerRegistration'
        request.session['REGISTRATION_FORM'] = 'mnd.forms.mnd_registration_form.MNDCarerRegistrationForm'
        url = reverse('registration_register', kwargs={'registry_code': registry_code})
        return redirect(url)


class PatientRegistrationView(RegistrationView):

    def get(self, request, registry_code):
        request.session['REGISTRATION_CLASS'] = 'mnd.registry.groups.registration.mnd_registration.MNDRegistration'
        request.session['REGISTRATION_FORM'] = 'mnd.forms.mnd_registration_form.MNDRegistrationForm'
        url = reverse('registration_register', kwargs={'registry_code': registry_code})
        return redirect(url)


class ApproveCarerView(LoginRequiredMixin, View):

    def carer_registration(self, primary_carer):
        return CarerRegistration.objects.filter(
            carer=primary_carer,
            expires_on__gte=timezone.now(),
            status=CarerRegistration.REGISTERED
        ).first()

    def primary_carer_str(self, primary_carer):
        return f"{primary_carer.first_name} {primary_carer.last_name} ({primary_carer.email})"

    def get(self, request):
        if not request.user.is_patient:
            return HttpResponseNotFound()
        patient = request.user.user_object.first()
        primary_carer = PrimaryCarer.objects.filter(patient_id=patient.id).first()
        if self.carer_registration(primary_carer):
            return render(
                request,
                "registration/approve_carer_registration.html",
                context={
                    "carer": self.primary_carer_str(primary_carer)
                }
            )

    def post(self, request):
        if not request.user.is_patient:
            return HttpResponseNotFound()
        has_approval = request.POST.get('approval', '').lower() == "yes"
        patient = request.user.user_object.first()
        primary_carer = PrimaryCarer.objects.filter(patient_id=patient.id).first()
        registration = self.carer_registration(primary_carer)
        if registration:
            registration.status = CarerRegistration.APPROVED if has_approval else CarerRegistration.REJECTED
            registration.save()
            CustomUser.objects.filter(carer_object=patient).update(is_active=True)
            return render(
                request,
                "registration/carer_registration_result.html",
                context={
                    "carer": self.primary_carer_str(primary_carer),
                    "result": _("approved") if has_approval else _("rejected")
                }
            )
