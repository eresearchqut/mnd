from datetime import timedelta
import uuid

from django.contrib.sites.models import Site
from django.forms import ValidationError
from django.http.response import HttpResponseForbidden
from django.shortcuts import render, redirect, reverse
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.translation import ugettext as _
from django.views import View

from registration.backends.default.views import RegistrationView
from rdrf.events.events import EventType
from rdrf.services.io.notifications.email_notification import process_notification


from ..registry.patients.mnd_admin_forms import PrimaryCarerForm
from registry.groups.models import CustomUser
from registry.patients.mixins import LoginRequiredMixin

from ..models import CarerRegistration, PrimaryCarer

import logging
logger = logging.getLogger(__name__)


class PatientCarerRegistrationView(LoginRequiredMixin, View):

    def primary_carer_str(self, primary_carer):
        return f"{primary_carer.first_name} {primary_carer.last_name} ({primary_carer.email})"

    def render_form(self, request, form, primary_carer, is_valid):
        return render(
            request,
            "registration/carer_enroll.html",
            context={
                "form": form,
                "carer": self.primary_carer_str(primary_carer),
                "valid": is_valid
            }
        )

    def has_existing_registration(self, primary_carer, patient):
        pending_carer = (
            CarerRegistration.objects.filter(
                carer=primary_carer,
                expires_on__gte=timezone.now(),
                status=CarerRegistration.CREATED
            ).exists()
        )
        registered_carer = (
            CarerRegistration.objects.filter(
                carer=primary_carer,
                patient=patient,
                status=CarerRegistration.REGISTERED
            ).exists()
        )
        return pending_carer or registered_carer

    def get_base_url(self):
        domain = Site.objects.get_current().domain
        protocol = "https"
        if domain == "localhost:8000":
            protocol = "http"
        return f"{protocol}://{domain}"

    def get(self, request):
        if not request.user.is_patient:
            return HttpResponseForbidden()
        patient = request.user.user_object.first()
        primary_carer = PrimaryCarer.objects.filter(patients__id=patient.id).first()
        is_valid = True
        if self.has_existing_registration(primary_carer, patient):
            form = PrimaryCarerForm(data=primary_carer.__dict__)
            form.add_error(None, ValidationError(_("A token was already generated for this carer !")))
            is_valid = False
        else:
            form = PrimaryCarerForm(instance=primary_carer)
        return self.render_form(request, form, primary_carer, is_valid)

    def post(self, request):
        if not request.user.is_patient:
            return HttpResponseForbidden()
        patient = request.user.user_object.first()
        primary_carer = PrimaryCarer.objects.filter(patients__id=patient.id).first()
        if self.has_existing_registration(primary_carer, patient):
            return HttpResponseForbidden()

        primary_carer_user = (
            CustomUser.objects
            .filter(email=primary_carer.email, patients_in_care__isnull=False)
            .distinct()
            .first()
        )
        registry_code = patient.rdrf_registry.first().code
        reg = CarerRegistration.objects.create(
            carer=primary_carer,
            patient=patient,
            token=uuid.uuid4(),
            expires_on=timezone.now() + timedelta(days=1)
        )
        if not primary_carer_user:
            registration_url = reverse('carer_registration', kwargs={"registry_code": registry_code})
            registration_full_url = f"{self.get_base_url()}{registration_url}?token={reg.token}&username={primary_carer.email}"

            template_data = {
                "primary_carer": primary_carer,
                "registration_url": registration_full_url,
                "patient": patient
            }
            process_notification(registry_code, EventType.NEW_CARER, template_data)
        else:
            template_data = {
                "primary_carer": primary_carer,
                "patient": patient
            }
            process_notification(registry_code, EventType.CARER_ASSIGNED, template_data)
            patient.carer = primary_carer_user
            patient.save(update_fields=['carer'])
            reg.registration_ts = timezone.now()
            reg.status = CarerRegistration.REGISTERED
            reg.save(update_fields=['status', 'registration_ts'])

        return render(
            request,
            "registration/carer_enroll_token.html",
            context={"email": primary_carer.email}
        )


class CarerRegistrationView(RegistrationView):

    def get(self, request, registry_code):
        request.session['REGISTRATION_CLASS'] = 'mnd.registry.groups.registration.mnd_registration.MNDCarerRegistration'
        request.session['REGISTRATION_FORM'] = 'mnd.forms.mnd_registration_form.MNDCarerRegistrationForm'
        params = urlencode(request.GET.dict())
        url = reverse('registration_register', kwargs={'registry_code': registry_code})
        return redirect(f"{url}?{params}") if params else redirect(url)


class PatientRegistrationView(RegistrationView):

    def get(self, request, registry_code):
        request.session['REGISTRATION_CLASS'] = 'mnd.registry.groups.registration.mnd_registration.MNDRegistration'
        request.session['REGISTRATION_FORM'] = 'mnd.forms.mnd_registration_form.MNDRegistrationForm'
        url = reverse('registration_register', kwargs={'registry_code': registry_code})
        return redirect(url)
