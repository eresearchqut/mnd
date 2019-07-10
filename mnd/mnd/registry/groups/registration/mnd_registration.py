import logging

from registry.groups.registration.patient import PatientRegistration
from registration.models import RegistrationProfile
from rdrf.events.events import EventType
from rdrf.services.io.notifications.email_notification import process_notification

from mnd.models import PatientInsurance, PrimaryCarer, PreferredContact

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

        form_data = self.form.cleaned_data
        preferred_contact = self._create_preferred_contact(patient)
        primary_carer = self._create_primary_carer(patient)
        patient_insurance = self._create_insurance_data(patient)

        if form_data['is_primary_carer']:
            preferred_contact.primary_carer = primary_carer

        template_data = {
            "patient": patient,
            "registration": RegistrationProfile.objects.get(user=user)
        }
        process_notification(registry_code, EventType.NEW_PATIENT, template_data)
        logger.debug("Registration process - sent notification for NEW_PATIENT")

    def get_template_name(self):
        return "registration/mnd_registration_form.html"

    def _create_insurance_data(self, patient):
        form_data = self.form.cleaned_data
        patient_insurace = PatientInsurance.objects.create(
            patient=patient,
            medicare_number=form_data["medicare_number"],
            pension_number=form_data["pension_number"],
            private_health_fund_name=form_data["insurer"],
            private_health_fund_number=form_data["health_fund_number"],
            ndis_number=form_data["ndis_number"],
            ndis_plan_manager=form_data["ndis_plan_manager"],
            ndis_coordinator_first_name=form_data["ndis_coordinator_first_name"],
            ndis_coordinator_last_name=form_data["ndis_coordinator_surname"],
            ndis_coordinator_phone=form_data["ndis_coordinator_phone"]
        )
        return patient_insurace

    def _create_preferred_contact(self, patient):
        form_data = self.form.cleaned_data
        preferred_contact = PreferredContact.objects.create(
            patient=patient,
            first_name=form_data["contact_first_name"],
            last_name=form_data["contact_surname"],
            phone=form_data["contact_phone"],
            contact_method=form_data["contact_method"]
        )
        return preferred_contact

    def _create_primary_carer(self, patient):
        form_data = self.form.cleaned_data

        primary_carer = PrimaryCarer.objects.create(
            patient=patient,
            first_name=form_data["primary_carer_first_name"],
            last_name=form_data["primary_carer_surname"],
            email=form_data['primary_carer_email'],
            phone=form_data['primary_carer_phone'],
            relationship=form_data['primary_carer_relationship']
        )
        return primary_carer
