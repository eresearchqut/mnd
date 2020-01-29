import logging

from registry.groups.registration.patient import PatientRegistration
from registration.models import RegistrationProfile
from rdrf.events.events import EventType
from rdrf.services.io.notifications.email_notification import process_notification

from registry.patients.models import Patient
from registry.patients.patient_stage_flows import get_registry_stage_flow

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

        registration = RegistrationProfile.objects.get(user=user)
        template_data = {
            "patient": patient,
            "registration": registration,
            "activation_url": self.get_registration_activation_url(registration),
        }

        process_notification(registry_code, EventType.NEW_PATIENT, template_data)
        logger.debug("Registration process - sent notification for NEW_PATIENT")

    def _create_patient(self, registry, working_group, user, set_link_to_user=True):
        form_data = self.form.cleaned_data
        patient = Patient.objects.create(
            consent=True,
            family_name=form_data["surname"],
            given_names=form_data["first_name"],
            date_of_birth=form_data["date_of_birth"],
            sex=form_data["gender"]
        )

        patient.rdrf_registry.add(registry)
        patient.working_groups.add(working_group)
        patient.email = user.username
        patient.user = user if set_link_to_user else None
        get_registry_stage_flow(registry).handle(patient)
        patient.save()
        return patient

    def get_template_name(self):
        return "registration/mnd_registration_form.html"
