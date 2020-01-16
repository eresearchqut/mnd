import logging

from django.utils import timezone

from registry.groups import GROUPS
from registry.groups.registration.base import BaseRegistration
from registry.groups.registration.patient import PatientRegistration
from registration.models import RegistrationProfile
from rdrf.events.events import EventType
from rdrf.services.io.notifications.email_notification import process_notification

from mnd.models import (
    CarerRegistration,
    PreferredContact,
    PatientInsurance,
    PrimaryCarer,
    PrimaryCarerRelationship
)

logger = logging.getLogger(__name__)


class MNDRegistration(PatientRegistration):

    def process(self, user):

        registry_code = self.form.cleaned_data['registry_code']
        registry = self._get_registry_object(registry_code)

        user = self.update_django_user(user, registry)

        working_group = self._get_unallocated_working_group(registry)
        user.working_groups.set([working_group])
        user.save()

        logger.debug("Registration process - created user")
        patient = self._create_patient(registry, working_group, user)
        logger.debug("Registration process - created patient")

        address = self._create_patient_address(patient)
        address.save()
        logger.debug("Registration process - created patient address")

        self._create_preferred_contact(patient)
        self._create_primary_carer(patient)
        self._create_insurance_data(patient)

        registration = RegistrationProfile.objects.get(user=user)
        template_data = {
            "patient": patient,
            "registration": registration,
            "activation_url": self.get_registration_activation_url(registration),
        }

        process_notification(registry_code, EventType.NEW_PATIENT, template_data)
        logger.debug("Registration process - sent notification for NEW_PATIENT")

    def get_template_name(self):
        return "registration/mnd_registration_form.html"

    def _create_insurance_data(self, patient):
        form_data = self.form.cleaned_data
        PatientInsurance.objects.create(
            patient=patient,
            medicare_number=form_data["patient_insurance_medicare_number"],
            pension_number=form_data["patient_insurance_pension_number"],
            private_health_fund=form_data["patient_insurance_private_health_fund"],
            private_health_fund_number=form_data["patient_insurance_private_health_fund_number"],
            ndis_number=form_data["patient_insurance_ndis_number"],
            ndis_plan_manager=form_data["patient_insurance_ndis_plan_manager"],
            ndis_coordinator_first_name=form_data["patient_insurance_ndis_coordinator_first_name"],
            ndis_coordinator_last_name=form_data["patient_insurance_ndis_coordinator_last_name"],
            ndis_coordinator_phone=form_data["patient_insurance_ndis_coordinator_phone"],
        )

    def _create_preferred_contact(self, patient):
        form_data = self.form.cleaned_data
        PreferredContact.objects.create(
            patient=patient,
            first_name=form_data["preferred_contact_first_name"],
            last_name=form_data["preferred_contact_last_name"],
            phone=form_data["preferred_contact_phone"],
            contact_method=form_data["preferred_contact_contact_method"]
        )

    def _create_primary_carer(self, patient):
        form_data = self.form.cleaned_data
        pc = None
        if form_data['primary_carer_email']:
            pc = PrimaryCarer.objects.filter(email=form_data['primary_carer_email']).first()
        if not pc:
            pc = PrimaryCarer.objects.create(
                first_name=form_data["primary_carer_first_name"],
                last_name=form_data["primary_carer_last_name"],
                email=form_data['primary_carer_email'],
                phone=form_data['primary_carer_phone'],
            )
        pc.patients.add(patient)
        PrimaryCarerRelationship.objects.create(
            carer=pc,
            patient=patient,
            relationship=form_data["primary_carer_relationship"],
            relationship_info=form_data["primary_carer_relationship_info"]
        )


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
        template_data = {
            "registration": registration,
            "activation_url": self.get_registration_activation_url(registration),
        }
        process_notification(registry_code, EventType.NEW_CARER, template_data)
        logger.debug("Registration process - sent notification for NEW_CARER")

    def update_django_user(self, django_user, registry):
        carer_registration = CarerRegistration.objects.get(token=self.form.cleaned_data['token'])
        carer_registration.status = CarerRegistration.REGISTERED
        carer_registration.registration_ts = timezone.now()
        carer_registration.save()
        pc = carer_registration.carer
        patient = carer_registration.patient
        patient.carer = django_user
        patient.save()
        return self.setup_django_user(django_user, registry, GROUPS.CARER, pc.first_name, pc.last_name)
