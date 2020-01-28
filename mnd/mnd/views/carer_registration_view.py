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


class RegistrationChecks:

    def __init__(self, primary_carer, patient):
        self.primary_carer = primary_carer
        self.patient = patient

    def has_pending_registration(self):
        return CarerRegistration.objects.filter(
            carer=self.primary_carer, expires_on__gte=timezone.now(), status=CarerRegistration.CREATED
        ).exists()

    def has_registered_carer(self):
        return CarerRegistration.objects.filter(
            carer=self.primary_carer, patient=self.patient, status=CarerRegistration.REGISTERED
        ).exists()

    def has_deactivated_carer(self):
        return CarerRegistration.objects.filter(
            carer=self.primary_carer, patient=self.patient, status=CarerRegistration.DEACTIVATED
        ).exists()

    def has_expired_registration(self):
        return CarerRegistration.objects.filter(
            carer=self.primary_carer, expires_on__lt=timezone.now(), status=CarerRegistration.CREATED,
        ).exists()


class RegistrationFlags:

    def __init__(self):
        self.can_activate = False
        self.can_deactivate = False
        self.can_resend_invite = False
        self.can_register = False

    def update(self, primary_carer, patient):
        checks = RegistrationChecks(primary_carer, patient)
        self.can_activate = checks.has_deactivated_carer()
        self.can_deactivate = checks.has_registered_carer()
        self.can_resend_invite = checks.has_expired_registration()
        self.has_pending_registration = checks.has_pending_registration()
        self.can_register = not (
            self.has_pending_registration or self.can_deactivate or self.can_activate
        ) and primary_carer


class CarerOperations:

    def __init__(self, request, primary_carer, patient):
        self.request = request
        self.primary_carer = primary_carer
        self.patient = patient

    def _get_base_url(self):
        domain = Site.objects.get_current().domain
        protocol = "https"
        if domain == "localhost:8000":
            protocol = "http"
        return f"{protocol}://{domain}"

    def deactivate_carer(self):
        self.patient.carer = None
        self.patient.save(update_fields=['carer'])
        CarerRegistration.objects.filter(
            carer=self.primary_carer, patient=self.patient, status=CarerRegistration.REGISTERED
        ).update(status=CarerRegistration.DEACTIVATED)
        template_data = {
            "primary_carer": self.primary_carer,
            "patient": self.patient
        }
        registry_code = self.patient.rdrf_registry.first().code
        process_notification(registry_code, EventType.CARER_DEACTIVATED, template_data)
        return render(
            self.request,
            "registration/carer_activate_deactivate.html",
            context={"email": self.primary_carer.email, "status": "deactivated"}
        )

    def activate_carer(self):
        self.patient.carer = CustomUser.objects.get(email=self.primary_carer.email)
        self.patient.save(update_fields=['carer'])
        CarerRegistration.objects.filter(
            carer=self.primary_carer, patient=self.patient, status=CarerRegistration.DEACTIVATED
        ).update(status=CarerRegistration.REGISTERED)
        template_data = {
            "primary_carer": self.primary_carer,
            "patient": self.patient
        }
        registry_code = self.patient.rdrf_registry.first().code
        process_notification(registry_code, EventType.CARER_ACTIVATED, template_data)
        return render(
            self.request,
            "registration/carer_activate_deactivate.html",
            context={"email": self.primary_carer.email, "status": "activated"}
        )

    def register_carer(self):
        primary_carer_user = (
            CustomUser.objects
            .filter(email=self.primary_carer.email, patients_in_care__isnull=False)
            .distinct()
            .first()
        )
        registry_code = self.patient.rdrf_registry.first().code
        reg = CarerRegistration.objects.create(
            carer=self.primary_carer,
            patient=self.patient,
            token=uuid.uuid4(),
            expires_on=timezone.now() + timedelta(days=2)
        )
        if not primary_carer_user:
            registration_url = reverse('carer_registration', kwargs={"registry_code": registry_code})
            registration_params = f"?token={reg.token}&username={self.primary_carer.email}"
            registration_full_url = f"{self._get_base_url()}{registration_url}{registration_params}"

            template_data = {
                "primary_carer": self.primary_carer,
                "registration_url": registration_full_url,
                "patient": self.patient
            }
            process_notification(registry_code, EventType.NEW_CARER, template_data)
        else:
            template_data = {
                "primary_carer": self.primary_carer,
                "patient": self.patient
            }
            process_notification(registry_code, EventType.CARER_ASSIGNED, template_data)
            self.patient.carer = primary_carer_user
            self.patient.save(update_fields=['carer'])
            reg.registration_ts = timezone.now()
            reg.status = CarerRegistration.REGISTERED
            reg.save(update_fields=['status', 'registration_ts'])

        return render(
            self.request,
            "registration/carer_enroll_token.html",
            context={"email": self.primary_carer.email}
        )


class PatientCarerRegistrationView(LoginRequiredMixin, View):

    def primary_carer_str(self, primary_carer):
        if primary_carer:
            return f"{primary_carer.first_name} {primary_carer.last_name} ({primary_carer.email})"
        else:
            return _("No primary carer set !")

    def render_form(self, request, form, primary_carer, flags):
        return render(
            request,
            "registration/carer_enroll.html",
            context={
                "form": form,
                "carer": self.primary_carer_str(primary_carer),
                "flags": flags,
            }
        )

    def get(self, request):
        if not request.user.is_patient:
            return HttpResponseForbidden()
        patient = request.user.user_object.first()
        primary_carer = PrimaryCarer.objects.filter(patients__id=patient.id).first()
        flags = RegistrationFlags()
        flags.update(primary_carer, patient)
        if not flags.can_register:
            form = PrimaryCarerForm(data=primary_carer.__dict__) if primary_carer else PrimaryCarerForm(data={})
            if not (flags.can_deactivate or flags.can_activate):
                if primary_carer:
                    form.add_error(None, ValidationError(_("A token was already generated for this carer !")))
                else:
                    form.add_error(None, ValidationError(_("Primary carer need to be set in order to register it !")))
        else:
            form = PrimaryCarerForm(instance=primary_carer)
        return self.render_form(request, form, primary_carer, flags)

    def post(self, request):
        if not request.user.is_patient:
            return HttpResponseForbidden()
        patient = request.user.user_object.first()
        primary_carer = PrimaryCarer.objects.filter(patients__id=patient.id).first()
        checks = RegistrationChecks(primary_carer, patient)
        operations = CarerOperations(request, primary_carer, patient)
        if checks.has_pending_registration():
            return HttpResponseForbidden()

        if checks.has_registered_carer():
            return operations.deactivate_carer()

        if checks.has_deactivated_carer():
            return operations.activate_carer()

        # resending email invite for expired carers
        # is the same as registering a carer
        return operations.register_carer()


class CarerRegistrationView(RegistrationView):

    def get(self, request, registry_code):
        request.session['REGISTRATION_CLASS'] = 'mnd.registry.groups.registration.mnd_registration.MNDCarerRegistration'
        request.session['REGISTRATION_FORM'] = 'mnd.forms.mnd_registration_form.MNDCarerRegistrationForm'
        params = urlencode(request.GET.dict())
        url = reverse('registration_register', kwargs={'registry_code': registry_code})
        return redirect(f"{url}?{params}") if params else redirect(url)
