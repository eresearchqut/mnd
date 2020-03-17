from django.utils.translation import ugettext as _

from rdrf.views.patient_view import (
    PatientFormMixin, AddPatientView as ParentAddPatientView, PatientEditView as ParentEditPatientView
)


from ..registry.patients.mnd_admin_forms import PatientInsuranceForm, PrimaryCarerForm, PreferredContactForm
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
                PrimaryCarerForm, _("Primary Carer"), "primary_carer", get_primary_carer(patient), request,
                get_primary_carer_initial_data(patient), patient
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
            get_form(
                PrimaryCarerForm, request, "primary_carer", get_primary_carer(instance),
                get_primary_carer_initial_data(instance), instance
            )
        )
        forms[self.PREFERRED_CONTACT_KEY] = (
            get_form(PreferredContactForm, request, "preferred_contact", get_preferred_contact(instance))
        )
        return forms

    def _handle_primary_carer_relationship(self, form, instance):
        email = form.cleaned_data['email']
        rel = form.cleaned_data.get('relationship')
        rel_info = form.cleaned_data.get('relationship_info')
        carer = instance or PrimaryCarer.objects.filter(email=email).first()
        if carer:
            pc, _ = PrimaryCarerRelationship.objects.get_or_create(patient=self.object)
            pc.carer = carer
            pc.relationship = rel
            pc.relationship_info = rel_info
            pc.save()
        return carer is not None

    def all_forms_valid(self, forms):
        ret_val = super().all_forms_valid(forms)
        formset_keys = [self.PATIENT_INSURANCE_KEY, self.PRIMARY_CARER_KEY, self.PREFERRED_CONTACT_KEY]
        for key in formset_keys:
            if key == self.PRIMARY_CARER_KEY:
                carer_handled = self._handle_primary_carer_relationship(forms[key], None)
                if carer_handled:
                    continue
            instance = forms[key].save(commit=False)
            instance.patient = self.object
            instance.save()
            if key == self.PRIMARY_CARER_KEY:
                self._handle_primary_carer_relationship(forms[key], instance)

        return ret_val


class AddPatientView(FormSectionMixin, ParentAddPatientView):
    pass


class PatientEditView(FormSectionMixin, ParentEditPatientView):
    pass
