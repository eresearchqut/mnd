import logging

from django.utils import timezone

from registry.groups import GROUPS
from registry.groups.registration.base import BaseRegistration
from registration.models import RegistrationProfile
from rdrf.events.events import EventType
from rdrf.services.io.notifications.email_notification import process_notification

from mnd.models import CarerRegistration

logger = logging.getLogger(__name__)


class MNDCarerRegistration(BaseRegistration):

    def get_template_name(self):
        return "registration/carer_registration_form.html"

    def process(self, user):
        logger.info(f"Carer registration process {user}")
        registry_code = self.form.cleaned_data['registry_code']
        registry = self._get_registry_object(registry_code)

        user = self.update_django_user(user, registry)

        working_group = self._get_unallocated_working_group(registry)
        user.working_groups.set([working_group])
        user.save()

        registration = RegistrationProfile.objects.get(user=user)
        carer, patient = self.get_carer_and_patient()
        template_data = {
            "registration": registration,
            "registration_url": self.get_registration_activation_url(registration),
            "primary_carer": carer,
            "patient": patient
        }
        process_notification(registry_code, EventType.NEW_CARER, template_data)
        logger.info("Registration process - sent notification for NEW_CARER")

    def get_carer_and_patient(self):
        carer_registration = CarerRegistration.objects.get(token=self.form.cleaned_data['token'])
        return carer_registration.carer, carer_registration.patient

    def update_django_user(self, django_user, registry):
        carer_registration = CarerRegistration.objects.get(token=self.form.cleaned_data['token'])
        carer_email = carer_registration.carer_email
        carer_registration.status = CarerRegistration.REGISTERED
        carer_registration.registration_ts = timezone.now()
        carer_registration.save()
        pc = carer_registration.carer
        patient = carer_registration.patient
        patient.carer = django_user
        patient.save()
        user = self.setup_django_user(django_user, registry, GROUPS.CARER, pc.first_name, pc.last_name)
        # check if there are other pending registrations for the same email address and if yes
        # automatically register those
        pending_registrations = (
            CarerRegistration.objects.filter(
                carer_email__iexact=carer_email,
                status=CarerRegistration.CREATED,
                expires_on__gte=timezone.now()
            ).exclude(pk=carer_registration.pk)
        )
        for reg in pending_registrations:
            reg.status = CarerRegistration.REGISTERED
            reg.registration_ts = timezone.now()
            reg.save()
            patient = reg.patient
            patient.carer = user
            patient.save()
        return user
