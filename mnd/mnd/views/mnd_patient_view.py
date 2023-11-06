from django.utils.translation import gettext as _
from django.db import transaction

from rdrf.events.events import EventType
from rdrf.helpers.constants import PATIENT_PERSONAL_DETAILS_SECTION_NAME
from rdrf.services.io.notifications.email_notification import process_notification
from rdrf.views.patient_view import (
    PatientFormMixin, AddPatientView as ParentAddPatientView, PatientEditView as ParentEditPatientView
)
from rdrf.helpers.form_section_helper import DemographicsSectionFieldBuilder

from ..registry.patients.mnd_admin_forms import (
    PatientInsuranceForm, PrimaryCarerForm, PreferredContactForm,
    DuplicatePatientForm, PatientLanguageForm
)
from ..models import PrimaryCarer, PrimaryCarerRelationship

import logging
logger = logging.getLogger(__name__)


def get_section(form, section_name, section_prefix, instance, request, initial=None, patient=None):
    if request.POST:
        form_instance = form(request.POST, prefix=section_prefix, instance=instance, initial=initial or {})
    else:
        form_instance = form(initial=initial or {}, prefix=section_prefix, instance=instance)

    if patient:
        form_instance.set_patient(patient)

    section = (section_name, [f for f in form_instance.fields])
    return form_instance, (section,)


def get_form(form, request, prefix, instance=None, initial=None, patient=None):
    form_instance = form(request.POST, prefix=prefix, instance=instance, initial=initial or {})
    if patient:
        form_instance.set_patient(patient)
    return form_instance


def get_insurance_data(patient):
    return getattr(patient, 'insurance_data', None)


def get_primary_carer(patient):
    return PrimaryCarer.get_primary_carer(patient)


def get_duplicate_patient(patient):
    return getattr(patient, 'duplicate_patient', None)


def get_patient_language(patient):
    return getattr(patient, 'language_info', None)


def get_primary_carer_initial_data(patient):
    data = {}
    carer = get_primary_carer(patient)
    if carer and carer.relation.filter(patient=patient).exists():
        relation = carer.relation.filter(patient=patient).first()
        data['relationship'] = relation.relationship
        data['relationship_info'] = relation.relationship_info
    return data


def get_preferred_contact(patient):
    return getattr(patient, 'preferred_contact', None)


class MNDSectionFieldBuilder(DemographicsSectionFieldBuilder):

    def get_personal_detail_fields(self, registry_code):
        personal_fields = [
            "family_name",
            "given_names",
            "maiden_name",
            "umrn",
            "date_of_birth",
            "place_of_birth",
            "date_of_migration",
            "country_of_birth",
            "ethnic_origin",
            "sex",
            "living_status",
        ]
        return (_(PATIENT_PERSONAL_DETAILS_SECTION_NAME), personal_fields)

    def get_contact_details_fields(self):
        contact_details_fields = [
            "home_phone",
            "mobile_phone",
            "work_phone",
            "email",
        ]
        return _("Contact Details"), contact_details_fields


class FormSectionMixin(PatientFormMixin):

    PATIENT_INSURANCE_KEY = "patient_insurance_form"
    PRIMARY_CARER_KEY = "primary_carer_form"
    PREFERRED_CONTACT_KEY = "preferred_contact_form"
    DUPLICATE_PATIENT_KEY = "duplicate_patient_form"
    PATIENT_LANGUAGE_KEY = "patient_language_form"

    EMAILS_SAME_ERROR = "Patient email and principal carer email should not be the same"

    def get_form_sections(self, user, request, patient, registry, patient_form,
                          patient_address_form, patient_doctor_form, patient_relative_form,
                          builder, error_after_all_forms_are_valid=None):
        mnd_builder = MNDSectionFieldBuilder()
        form_sections = super().get_form_sections(
            user, request, patient, registry, patient_form,
            patient_address_form, patient_doctor_form, patient_relative_form,
            mnd_builder
        )
        for form_instance, __ in form_sections:
            if hasattr(form_instance, 'fields'):
                if 'umrn' in form_instance.fields:
                    form_instance.fields['umrn'].label = _("AMNDR ID")
                if 'working_groups' in form_instance.fields:
                    form_instance.fields['working_groups'].help_text = _('''
                    Please select the clinic that you attend or will attend.
                     If you do not attend a clinic, please leave as 'mnd Unallocated'.
                     Selecting a clinic means that your clinic can view and collect your clinical information.
                     To add an additional clinic, hold the ctrl / cmd key and select a clinic,
                     or contact your current clinic for assistance.
                    ''')
                if 'registered_clinicians' in form_instance.fields:
                    form_instance.fields['registered_clinicians'].help_text = _('''
                    Selecting a clinician from your clinic means that you allow them to see the data
                     you have entered yourself. To select multiple clinicians,
                     hold the ctrl / cmd key and click.
                     You can remove a clinician at any time to stop sharing your personal data,
                     this will not effect your clinical visit data.
                    ''')

        form_sections.insert(
            2,
            get_section(
                PatientLanguageForm, _("Language Info"), "language_info", get_patient_language(patient), request
            )
        )
        form_sections.insert(
            3,
            (patient_form, (mnd_builder.get_contact_details_fields(), ))
        )

        form_sections.insert(
            4,
            get_section(
                PreferredContactForm, _("Patient Preferred Contact Method "), "preferred_contact", get_preferred_contact(patient), request
            )
        )

        form_sections.extend([
            get_section(
                PatientInsuranceForm, _("Medicare, Health Insurance and Support details"), "patient_insurance", get_insurance_data(patient), request
            ),
            get_section(
                PrimaryCarerForm, _("Principal Carer"), "primary_carer", get_primary_carer(patient), request,
                get_primary_carer_initial_data(patient), patient
            ),
        ])

        if user.is_staff:
            form_sections.append(
                get_section(
                    DuplicatePatientForm, _("Potential duplicate"), "duplicate_patient", get_duplicate_patient(patient), request
                )
            )

        if error_after_all_forms_are_valid:
            for pair in form_sections:
                form = pair[0]
                if form.prefix == 'primary_carer':
                    form.add_error('email', error_after_all_forms_are_valid[0])
                    break

        return form_sections

    def get_forms(self, request, registry_model, user, instance=None):
        forms = super().get_forms(request, registry_model, user, instance)
        forms[self.PATIENT_LANGUAGE_KEY] = (
            get_form(PatientLanguageForm, request, "language_info", get_patient_language(instance))
        )
        forms[self.PATIENT_INSURANCE_KEY] = (
            get_form(PatientInsuranceForm, request, "patient_insurance", get_insurance_data(instance))
        )
        forms[self.PRIMARY_CARER_KEY] = (
            get_form(
                PrimaryCarerForm, request, "primary_carer", get_primary_carer(instance),
                get_primary_carer_initial_data(instance), instance
            )
        )
        forms[self.PREFERRED_CONTACT_KEY] = (
            get_form(PreferredContactForm, request, "preferred_contact", get_preferred_contact(instance))
        )
        forms[self.DUPLICATE_PATIENT_KEY] = (
            get_form(DuplicatePatientForm, request, "duplicate_patient", get_duplicate_patient(instance))
        )
        return forms

    def _handle_primary_carer_relationship(self, forms, form, instance):
        patient_form = forms['patient_form']
        if patient_form and patient_form.cleaned_data['email'] == form.cleaned_data['email']:
            patient_form.add_error('email', self.EMAILS_SAME_ERROR)
            return False

        rel = form.cleaned_data.get('relationship')
        rel_info = form.cleaned_data.get('relationship_info')
        carer = instance or PrimaryCarer.objects.filter(email__iexact=email).first()
        if carer:
            pc = PrimaryCarerRelationship.objects.filter(patient=self.object).first()
            if pc is None:
                pc = PrimaryCarerRelationship.objects.create(patient=self.object, carer=carer)
            else:
                pc.carer = carer
            pc.relationship = rel
            pc.relationship_info = rel_info
            pc.save()
        return carer is not None

    def _handle_duplicate_patients(self, form, instance):
        if 'is_duplicate' in form.changed_data and form.cleaned_data['is_duplicate']:
            registry_code = instance.patient.rdrf_registry.first().code
            process_notification(registry_code, EventType.DUPLICATE_PATIENT_SET,
                                 {"patient": instance.patient})

    def all_forms_valid(self, forms):
        try:
            with transaction.atomic():
                ret_val = super().all_forms_valid(forms)[1]
                formset_keys = [self.PATIENT_LANGUAGE_KEY, self.PATIENT_INSURANCE_KEY, self.PRIMARY_CARER_KEY,
                                self.PREFERRED_CONTACT_KEY, self.DUPLICATE_PATIENT_KEY]
                for key in formset_keys:
                    instance = forms[key].save(commit=False)
                    instance.patient = self.object
                    instance.save()
                    if key == self.PRIMARY_CARER_KEY:
                        if not self._handle_primary_carer_relationship(forms, forms[key], instance):
                            self.object = None
                            raise Exception(self.EMAILS_SAME_ERROR)
                    elif key == self.DUPLICATE_PATIENT_KEY:
                        self._handle_duplicate_patients(forms[key], instance)

                return True, ret_val
        except Exception as ex:
            return False, [str(ex)]

class AddPatientView(FormSectionMixin, ParentAddPatientView):
    pass


class PatientEditView(FormSectionMixin, ParentEditPatientView):
    pass
