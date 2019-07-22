import logging

from registry.groups.registration.patient import PatientRegistration
from registration.models import RegistrationProfile
from rdrf.events.events import EventType
from rdrf.services.io.notifications.email_notification import process_notification

from mnd.models import PatientInsurance, PrimaryCarer, PreferredContact, PrivateHealthFund

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
        health_fund_code = form_data["patient_insurance_private_health_fund"]
        patient_insurance = PatientInsurance.objects.create(
            patient=patient,
            medicare_number=form_data["patient_insurance_medicare_number"],
            pension_number=form_data["patient_insurance_pension_number"],
            private_health_fund_number=form_data["patient_insurance_private_health_fund_number"],
            ndis_number=form_data["patient_insurance_ndis_number"],
            ndis_plan_manager=form_data["patient_insurance_ndis_plan_manager"],
            ndis_coordinator_first_name=form_data["patient_insurance_ndis_coordinator_first_name"],
            ndis_coordinator_last_name=form_data["patient_insurance_ndis_coordinator_last_name"],
            ndis_coordinator_phone=form_data["patient_insurance_ndis_coordinator_phone"]
        )
        if health_fund_code and health_fund_code != "":
            patient_insurance.private_health_fund = PrivateHealthFund.objects.get(code=health_fund_code)
            patient_insurance.save()

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
        PrimaryCarer.objects.create(
            patient=patient,
            first_name=form_data["primary_carer_first_name"],
            last_name=form_data["primary_carer_last_name"],
            email=form_data['primary_carer_email'],
            phone=form_data['primary_carer_phone'],
            relationship=form_data['primary_carer_relationship'],
            relationship_info=form_data['primary_carer_relationship_info']
        )
