from collections import OrderedDict

from django.forms import CharField
from django.forms.widgets import  Select

from django.utils.translation import gettext as _

from rdrf.forms.registration_forms import PatientRegistrationForm

from mnd.registry.patients.mnd_admin_forms import PatientInsuranceForm, PreferredContactForm, PrimaryCarerForm


class MNDRegistrationForm(PatientRegistrationForm):

    parent_forms = OrderedDict({
        'patient_insurance': PatientInsuranceForm,
        'preferred_contact': PreferredContactForm,
        'primary_carer': PrimaryCarerForm})

    PatientRegistrationForm.placeholders.update({
        'preferred_contact_contact_method': _("Preferred contact method"),
        'preferred_contact_email': _("Email address"),
        'preferred_contact_first_name': _("Preferred contact first name"),
        'preferred_contact_last_name': _("Preferred contact family name"),
        'preferred_contact_phone': _("Preferred contact phone"),
        'patient_insurance_medicare_number': _("Medicare number"),
        'patient_insurance_pension_number': _("Pension number"),
        'patient_insurance_private_health_fund_number': _("Private Health fund number"),
        'patient_insurance_ndis_number': _("NDIS number"),
        'patient_insurance_ndis_coordinator_first_name': _("NDIS case coordinator first name"),
        'patient_insurance_ndis_coordinator_last_name': _("NDIS case coordinator family name"),
        'patient_insurance_ndis_coordinator_phone': _("NDIS case coordinator phone"),
        'primary_carer_first_name': _("Primary carer first name"),
        'primary_carer_last_name': _("Primary carer family name"),
        'primary_carer_phone': _("Primary carer phone"),
        'primary_carer_email': _("Primary carer email"),
        'primary_carer_relationship_info': _("Specify relation to primary carer")

    })

    patient_insurance_private_health_fund = CharField(widget=Select)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for prefix, form in self.parent_forms.items():
            for name, value in form().fields.items():
                self.fields[f"{prefix}_{name}"] = value
        self.setup_fields()

    def _clean_fields(self):
        health_fund_set = self.data.get('patient_insurance_private_health_fund', '') != ''
        self.fields['patient_insurance_private_health_fund_number'].required = health_fund_set

        ndis_number_set = self.data.get('patient_insurance_ndis_number', '') != ''
        self.fields['patient_insurance_ndis_plan_manager'].required = ndis_number_set
        if self.data.get('patient_insurance_ndis_plan_manager', '') == 'other':
            for f in ['patient_insurance_ndis_coordinator_first_name',
                      'patient_insurance_ndis_coordinator_surname',
                      'patient_insurance_ndis_coordinator_phone']:
                self.fields[f].required = ndis_number_set
        super()._clean_fields()