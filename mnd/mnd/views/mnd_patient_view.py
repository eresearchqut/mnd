from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _

from rdrf.views.patient_view import (
    PatientFormMixin, AddPatientView as ParentAddPatientView, PatientEditView as ParentEditPatientView
)

from registry.patients.models import Patient

from ..models import PatientInsurance, PrimaryCarer, PreferredContact
from ..registry.patients.mnd_admin_forms import PatientInsuranceForm, PrimaryCarerForm, PreferredContactForm

import logging
logger = logging.getLogger(__name__)


def get_section(patient, model, form, section_name, section_prefix):
    formset = inlineformset_factory(Patient,
                                    model,
                                    form=form,
                                    min_num=1,
                                    max_num=1,
                                    extra=0,
                                    can_delete=False,
                                    validate_min=True,
                                    validate_max=True,
                                    fields="__all__")

    result_form = formset(instance=patient, prefix=section_prefix)
    section = (section_name, None)
    return result_form, (section,)


def get_formset(model, form, request, prefix, instance=None):
    formset = inlineformset_factory(
        Patient, model, form=form, fields="__all__"
    )
    return formset(request.POST, instance=instance, prefix=prefix)


class FormSectionMixin(PatientFormMixin):

    PATIENT_INSURANCE_KEY = "patient_insurance_form"
    PRIMARY_CARER_KEY = "primary_carer_form"
    PREFERRED_CONTACT_KEY = "preferred_contact_form"

    EXCLUDED_SECTIONS = [_("Next of Kin")]
    EXCLUDED_FIELDS = [
        "maiden_name", "umrn", "place_of_birth", "date_of_migration", "country_of_birth", "ethnic_origin",
    ]

    def get_form_sections(self, user, patient, registry, registry_code, patient_form,
                          patient_address_form, patient_doctor_form, patient_relative_form):

        def filter_fields(fields):
            return [f for f in fields if f not in self.EXCLUDED_FIELDS] if fields else None

        form_sections = super().get_form_sections(
            user, patient, registry, registry_code, patient_form,
            patient_address_form, patient_doctor_form, patient_relative_form
        )

        filtered_sections = [
            (result_form, ((section_name, filter_fields(fields)),)) for result_form, ((section_name, fields),)
            in form_sections if section_name not in self.EXCLUDED_SECTIONS
        ]

        filtered_sections.extend([
            get_section(patient, PatientInsurance, PatientInsuranceForm, _("Patient Insurance"), "patient_insurance"),
            get_section(patient, PrimaryCarer, PrimaryCarerForm, _("Primary Carer"), "primary_carer"),
            get_section(patient, PreferredContact, PreferredContactForm, _("Preferred Contact"), "preferred_contact")
        ])
        return filtered_sections

    def get_forms(self, request, registry_model, user, instance=None):
        forms = super().get_forms(request, registry_model, user, instance)
        forms[self.PATIENT_INSURANCE_KEY] = (
            get_formset(PatientInsurance, PatientInsuranceForm, request, "patient_insurance", instance)
        )
        forms[self.PRIMARY_CARER_KEY] = (
            get_formset(PrimaryCarer, PrimaryCarerForm, request, "primary_carer", instance)
        )
        forms[self.PREFERRED_CONTACT_KEY] = (
            get_formset(PreferredContact, PreferredContactForm, request, "preferred_contact", instance)
        )
        return forms

    def all_forms_valid(self, forms):
        ret_val = super().all_forms_valid(forms)
        formset_keys = [self.PATIENT_INSURANCE_KEY, self.PRIMARY_CARER_KEY, self.PREFERRED_CONTACT_KEY]
        for key in formset_keys:
            formset = forms[key]
            formset.instance = self.object
            formset_models = formset.save()
            for model_instance in formset_models:
                model_instance.patient = self.object
                model_instance.save()
                break
        return ret_val


class AddPatientView(FormSectionMixin, ParentAddPatientView):
    pass


class PatientEditView(FormSectionMixin, ParentEditPatientView):
    pass
