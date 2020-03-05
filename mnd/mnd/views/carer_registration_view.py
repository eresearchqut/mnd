from datetime import timedelta
import uuid

from django.conf import settings
from django.contrib import messages
from django.http.response import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.views import View

from rdrf.events.events import EventType
from rdrf.services.io.notifications.email_notification import process_notification


from registry.groups.models import CustomUser
from registry.groups.registration.base import BaseRegistration
from registry.patients.mixins import LoginRequiredMixin
from registry.patients.models import Patient


from ..models import CarerRegistration, PrimaryCarer

import logging
logger = logging.getLogger(__name__)


class RegistrationFlags:

    def __init__(self, primary_carer, patient):
        self.primary_carer = primary_carer
        self.patient = patient

    @cached_property
    def can_activate(self):
        return CarerRegistration.objects.has_deactivated_carer(self.primary_carer, self.patient)

    @cached_property
    def can_deactivate(self):
        return CarerRegistration.objects.has_registered_carer(self.primary_carer, self.patient)

    @cached_property
    def has_expired_registration(self):
        return CarerRegistration.objects.has_expired_registration(self.primary_carer)

    @cached_property
    def has_pending_registration(self):
        return CarerRegistration.objects.has_pending_registration(self.primary_carer)

    @cached_property
    def is_carer_registered(self):
        return CarerRegistration.objects.is_carer_registered(self.primary_carer)

    @cached_property
    def can_register(self):
        return not (
            self.has_pending_registration or self.can_deactivate or self.can_activate
        ) and self.primary_carer

    @cached_property
    def no_activation(self):
        return not (self.can_deactivate or self.can_activate)

    @cached_property
    def token_already_generated(self):
        return self.primary_carer and self.no_activation and self.has_pending_registration

    @cached_property
    def no_primary_carer_set(self):
        return self.no_activation and not self.primary_carer

    @cached_property
    def registration_allowed(self):
        registry = self.patient.rdrf_registry.first()
        if registry:
            return registry.carer_registration_allowed()
        return False


class CarerOperations:

    def __init__(self, request, primary_carer, patient, is_carer=False):
        self.request = request
        self.primary_carer = primary_carer
        self.patient = patient
        self.is_carer = is_carer

    def deactivate_carer(self):
        self.patient.carer = None
        self.patient.save(update_fields=['carer'])
        CarerRegistration.objects.filter(
            carer=self.primary_carer, patient=self.patient, status=CarerRegistration.REGISTERED
        ).update(status=CarerRegistration.DEACTIVATED)
        template_data = {
            "primary_carer": self.primary_carer,
            "patient": self.patient,
            "user": self.request.user
        }
        registry_code = self.patient.rdrf_registry.first().code
        process_notification(registry_code, EventType.CARER_DEACTIVATED, template_data)
        if not self.is_carer:
            return render(
                self.request,
                "registration/carer_activate_deactivate.html",
                context={"email": self.primary_carer.email, "status": "deactivated"}
            )
        else:
            return HttpResponseRedirect(reverse('patientslisting'))

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
        # TODO patients_in_care isnull shouldn't be needed?
        primary_carer_user = (
            CustomUser.objects
            .filter(username=self.primary_carer.email, patients_in_care__isnull=False)
            .distinct()
            .first()
        )
        registry_code = self.patient.rdrf_registry.first().code

        reg = CarerRegistration.objects.get_pending_registration(self.primary_carer)
        if reg is None:
            reg = CarerRegistration.objects.create(
                carer=self.primary_carer,
                patient=self.patient,
                token=uuid.uuid4(),
                expires_on=timezone.now() + timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
            )
        else:
            reg.expires_on = timezone.now() + timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
            reg.save()

        if not primary_carer_user:
            registration_url = reverse('carer_registration', kwargs={"registry_code": registry_code})
            registration_params = f"?token={reg.token}&username={self.primary_carer.email}"
            registration_full_url = f"{BaseRegistration.get_base_url()}{registration_url}{registration_params}"

            template_data = {
                "primary_carer": self.primary_carer,
                "registration_url": registration_full_url,
                "patient": self.patient
            }
            process_notification(registry_code, EventType.CARER_INVITED, template_data)
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

        # TODO no rendering in any of the operation methods
        # just put in the right message and return
        return render(
            self.request,
            "registration/carer_enrol_token.html",
            context={"email": self.primary_carer.email}
        )


class PatientCarerRegistrationView(LoginRequiredMixin, View):

    def primary_carer_str(self, primary_carer):
        if primary_carer:
            return f"{primary_carer.first_name} {primary_carer.last_name} ({primary_carer.email})"
        else:
            return _("unset")

    def get(self, request):
        if not request.user.is_patient:
            return HttpResponseForbidden()
        patient = request.user.user_object.first()
        primary_carer = PrimaryCarer.get_primary_carer(patient)
        flags = RegistrationFlags(primary_carer, patient)

        return self._render(request, patient, primary_carer, flags)

    def post(self, request):
        if not request.user.is_patient:
            return HttpResponseForbidden()
        patient = request.user.user_object.first()
        primary_carer = PrimaryCarer.get_primary_carer(patient)
        operations = CarerOperations(request, primary_carer, patient)
        flags = RegistrationFlags(primary_carer, patient)
        # if flags.has_pending_registration:
        #    return HttpResponseForbidden()

        if flags.can_deactivate:
            return operations.deactivate_carer()

        if flags.can_activate:
            return operations.activate_carer()

        # resending email invite for expired carers
        # is the same as registering a carer
        operations.register_carer()

        messages.success(request, _(f"Email invitation sent to {primary_carer.email}."))

        return self._render(request, patient, primary_carer, flags)

    def _render(self, request, patient, primary_carer, flags):
        registry = patient.user.registry.first()
        return render(
            request,
            "registration/carer_enrol.html",
            context={
                "patient": patient,
                "registry_code": registry.code,
                "carer": self.primary_carer_str(primary_carer),
                "flags": flags,
                })


class CarerOperationsView(LoginRequiredMixin, View):

    def get(self, request):
        if not request.user.is_carer:
            return HttpResponseForbidden()
        patients = request.user.patients_in_care.all()
        primary_carer = PrimaryCarer.objects.get(email=request.user.email)
        return render(
            request,
            "registration/carer_operations.html",
            context={
                "carer": primary_carer,
                "patients": patients
            }
        )

    def post(self, request):
        if not request.user.is_carer:
            return HttpResponseForbidden()
        primary_carer = PrimaryCarer.objects.get(email=request.user.email)
        patient_id = request.POST.get('patient_id', None)
        if patient_id:
            patient = Patient.objects.get(pk=patient_id)
            operations = CarerOperations(request, primary_carer, patient, is_carer=True)
            return operations.deactivate_carer()
        else:
            return HttpResponseRedirect(reverse('patientslisting'))
