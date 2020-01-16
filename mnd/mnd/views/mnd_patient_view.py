from django.utils.translation import ugettext as _

from rdrf.views.patient_view import (
    PatientFormMixin, AddPatientView as ParentAddPatientView, PatientEditView as ParentEditPatientView
)


from ..registry.patients.mnd_admin_forms import PatientInsuranceForm, PrimaryCarerForm, PreferredContactForm

import logging
logger = logging.getLogger(__name__)


def get_section(form, section_name, section_prefix, instance, request):
    if request.POST:
        form_instance = form(data=request.POST, prefix=section_prefix)
    else:
        form_instance = form(prefix=section_prefix, instance=instance)

    section = (section_name, [f for f in form_instance.fields])
    return form_instance, (section,)


def get_form(form, request, prefix, instance=None):
    return form(request.POST, prefix=prefix, instance=instance)


def get_insurance_data(patient):
    return getattr(patient, 'insurance_data', None)


def get_primary_carer(patient):
    carer = patient.primary_carers.first()
    if carer and carer.relation.exists():
        relation = carer.relation.filter(patient=patient).first()
        setattr(carer, 'relationship', relation.relationship)
        setattr(carer, 'relationship_info', relation.relationship_info)
    return carer


def get_preferred_contact(patient):
    return getattr(patient, 'preferred_contact', None)


class FormSectionMixin(PatientFormMixin):

    PATIENT_INSURANCE_KEY = "patient_insurance_form"
    PRIMARY_CARER_KEY = "primary_carer_form"
    PREFERRED_CONTACT_KEY = "preferred_contact_form"

    def get_form_sections(self, user, request, patient, registry, registry_code, patient_form,
                          patient_address_form, patient_doctor_form, patient_relative_form):

        form_sections = super().get_form_sections(
            user, request, patient, registry, registry_code, patient_form,
            patient_address_form, patient_doctor_form, patient_relative_form
        )
        for form_instance, __ in form_sections:
            if 'umrn' in form_instance.fields:
                form_instance.fields['umrn'].label = _("AMNDR / Hospital ID")
                break

        form_sections.extend([
            get_section(
                PatientInsuranceForm, _("Patient Insurance"), "patient_insurance", get_insurance_data(patient), request
            ),
            get_section(
                PrimaryCarerForm, _("Primary Carer"), "primary_carer", get_primary_carer(patient), request
            ),
            get_section(
                PreferredContactForm, _("Preferred Contact"), "preferred_contact", get_preferred_contact(patient), request
            )
        ])
        return form_sections

    def get_forms(self, request, registry_model, user, instance=None):
        forms = super().get_forms(request, registry_model, user, instance)
        forms[self.PATIENT_INSURANCE_KEY] = (
            get_form(PatientInsuranceForm, request, "patient_insurance", get_insurance_data(instance))
        )
        forms[self.PRIMARY_CARER_KEY] = (
            get_form(PrimaryCarerForm, request, "primary_carer", get_primary_carer(instance))
        )
        forms[self.PREFERRED_CONTACT_KEY] = (
            get_form(PreferredContactForm, request, "preferred_contact", get_preferred_contact(instance))
        )
        return forms

    def all_forms_valid(self, forms):
        ret_val = super().all_forms_valid(forms)
        formset_keys = [self.PATIENT_INSURANCE_KEY, self.PRIMARY_CARER_KEY, self.PREFERRED_CONTACT_KEY]
        for key in formset_keys:
            instance = forms[key].save(commit=False)
            instance.patient = self.object
            instance.save()

        return ret_val


class AddPatientView(FormSectionMixin, ParentAddPatientView):
    pass


class PatientEditView(FormSectionMixin, ParentEditPatientView):
    pass
