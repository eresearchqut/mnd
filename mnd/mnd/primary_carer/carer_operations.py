from datetime import timedelta
import logging
import uuid

from django.conf import settings
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _

from registry.groups.models import CustomUser
from registry.groups.registration.base import BaseRegistration

from rdrf.events.events import EventType
from rdrf.services.io.notifications.email_notification import process_notification

from ..models import CarerRegistration
from .utils import primary_carer_str


logger = logging.getLogger(__name__)


class CarerOperationResult:

    def __init__(self, context, message, state, operation_result=True):
        self.context = context
        self.operation_result = operation_result
        self.message = message
        self.state = state
        self.template = state.template()


class CarerOperations:

    def __init__(self, request, state):
        self.request = request
        self.primary_carer = state.carer
        self.patient = state.patient
        self.template = state.template()
        self.state = state

    def _setup_context(self, event_type=None, status=None):
        context = {}
        registry = self.patient.rdrf_registry.first() if self.patient else None
        context = {
            "email": self.primary_carer.email if self.primary_carer else None,
            "carer": _(primary_carer_str(self.primary_carer)),
            "patient": self.patient,
            "registry_code": registry.code if registry else None,
        }
        if event_type and registry:
            context.update({
                'notification_configured': registry.has_email_notification(event_type)
            })
        if status:
            context.update({'status': status})
        return context

    def nop(self, event_type=None):
        '''
        Default no operation
        '''
        return CarerOperationResult(
            context=self._setup_context(event_type=event_type),
            message=None,
            state=self.state
        )

    def _handle_notification_result(self, event_type, email_sent, has_disabled_notification, success_message):
        if not email_sent:
            message = _(f"Failure while sending email to {self.primary_carer.email}!")
            success = False
        elif has_disabled_notification:
            message = _(f"The notification for {event_type} is disabled!")
            success = False
        else:
            message = success_message
            success = True
        return success, message

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
        registry = self.patient.rdrf_registry.first()
        email_sent, has_disabled_notification = process_notification(registry.code, EventType.CARER_DEACTIVATED, template_data)
        success_message = _(f"{primary_carer_str(self.primary_carer)} deactivated!")
        success, message = self._handle_notification_result(
            EventType.CARER_DEACTIVATED, email_sent, has_disabled_notification, success_message
        )
        return CarerOperationResult(
            context=self._setup_context(event_type=EventType.CARER_DEACTIVATED, status="deactivated"),
            message=message,
            state=self.state.next_state(),
            operation_result=success
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
        email_sent, has_disabled_notification = process_notification(registry_code, EventType.CARER_ACTIVATED, template_data)
        success_message = _(f"{primary_carer_str(self.primary_carer)} activated!")
        success, message = self._handle_notification_result(
            EventType.CARER_ACTIVATED, email_sent, has_disabled_notification, success_message
        )
        return CarerOperationResult(
            context=self._setup_context(event_type=EventType.CARER_ACTIVATED, status="deactivated"),
            message=message,
            state=self.state.next_state(),
            operation_result=success
        )

    def register_carer(self):
        primary_carer_user = (
            CustomUser.objects
            .filter(username=self.primary_carer.email)
            .distinct()
            .first()
        )
        registry_code = self.patient.rdrf_registry.first().code

        reg = CarerRegistration.objects.get_pending_registration(self.primary_carer, patient=self.patient)
        if reg is None:
            reg = CarerRegistration.objects.create(
                carer=self.primary_carer,
                patient=self.patient,
                carer_email=self.primary_carer.email,
                token=uuid.uuid4(),
                expires_on=timezone.now() + timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
            )
            # if there are expired registrations for this carer and patient delete them
            CarerRegistration.objects.filter(
                carer=self.primary_carer,
                patient=self.patient,
                status=CarerRegistration.CREATED,
                expires_on__lte=timezone.now()
            ).delete()
        else:
            reg.expires_on = reg.expires_on + timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
            reg.save()

        message = ""
        success = True
        if not primary_carer_user:
            registration_url = reverse('carer_registration', kwargs={"registry_code": registry_code})
            registration_params = f"?token={reg.token}&username={self.primary_carer.email}"
            registration_full_url = f"{BaseRegistration.get_base_url()}{registration_url}{registration_params}"

            template_data = {
                "primary_carer": self.primary_carer,
                "registration_url": registration_full_url,
                "patient": self.patient
            }
            email_sent, has_disabled_notification = process_notification(registry_code, EventType.CARER_INVITED, template_data)
            success_message = _(f"{primary_carer_str(self.primary_carer)} invited!")
            success, message = self._handle_notification_result(
                EventType.CARER_INVITED, email_sent, has_disabled_notification, success_message
            )
        else:
            template_data = {
                "primary_carer": self.primary_carer,
                "patient": self.patient
            }
            email_sent, has_disabled_notification = process_notification(registry_code, EventType.CARER_ASSIGNED, template_data)
            success_message = _(f"{primary_carer_str(self.primary_carer)} assigned!")
            success, message = self._handle_notification_result(
                EventType.CARER_ASSIGNED, email_sent, has_disabled_notification, success_message
            )
            self.patient.carer = primary_carer_user
            self.patient.save(update_fields=['carer'])
            reg.registration_ts = timezone.now()
            reg.status = CarerRegistration.REGISTERED
            reg.save(update_fields=['status', 'registration_ts'])

        return CarerOperationResult(
            context=self._setup_context(),
            message=message,
            state=self.state.next_state(),
            operation_result=success
        )
