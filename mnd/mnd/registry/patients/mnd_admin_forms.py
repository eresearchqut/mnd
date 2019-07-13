from django import forms
from django.forms.utils import ErrorDict
from django.utils.translation import ugettext as _

from mnd.models import PatientInsurance, PrimaryCarer, PreferredContact


class PrefixedModelForm(forms.ModelForm):

    def field_name(self, name):
        return f"{self.prefix}-{name}" if self.prefix else name

    def clean(self):
        prefix = self.prefix
        ret_val = super().clean()
        new_fields = ErrorDict()
        for k, v in self.errors.items():
            new_fields[f"{prefix}-{k}"] = v
        self._errors = new_fields
        return ret_val


class PatientInsuranceForm(PrefixedModelForm):
    class Meta:
        model = PatientInsurance
        fields = ('medicare_number', 'pension_number', 'private_health_fund', 'private_health_fund_number',
                  'ndis_number', 'ndis_plan_manager', 'ndis_coordinator_first_name',
                  'ndis_coordinator_last_name', 'ndis_coordinator_phone')
        labels = {
            'ndis_number': _('NDIS number'),
            'ndis_plan_manager': _('NDIS Plan Manager'),
            'ndis_coordinator_first_name': _('NDIS Coordinator first name'),
            'ndis_coordinator_last_name': _('NDIS Coordinator last name'),
            'ndis_coordinator_phone': _('NDIS Coordinator phone')
        }

    def _clean_fields(self):

        health_fund_number_set = self.data.get(self.field_name('private_health_fund'), '').strip() != ''
        self.fields['private_health_fund'].required = health_fund_number_set
        self.fields['pension_number'].required = not health_fund_number_set
        ndis_number_set = self.data.get(self.field_name('ndis_number'), '').strip() != ''
        self.fields['private_health_fund'].required = not ndis_number_set
        self.fields['private_health_fund_number'].required = not ndis_number_set
        ndis_coordinator_info = [
            'ndis_coordinator_first_name', 'ndis_coordinator_last_name', 'ndis_coordinator_phone'
        ]
        coordinator_required_data = self.data.get(self.field_name('ndis_plan_manager'), '').strip() == 'other'
        for f in ndis_coordinator_info:
            self.fields[f].required = coordinator_required_data
        super()._clean_fields()


class PrimaryCarerForm(PrefixedModelForm):

    class Meta:
        model = PrimaryCarer
        fields = ('first_name', 'last_name', 'phone', 'email', 'relationship', 'relationship_info')

    def _clean_fields(self):
        required_relationship_info = self.data.get(self.field_name('relationship'), '').strip() == 'other'
        self.fields['relationship_info'].required = required_relationship_info
        super()._clean_fields()


class PreferredContactForm(PrefixedModelForm):
    class Meta:
        model = PreferredContact
        fields = ('first_name', 'last_name', 'phone', 'email', 'contact_method')

    def _clean_fields(self):
        required_info = self.data.get(self.field_name('contact_method'), '').strip() == 'person'
        if required_info:
            required_fields = ['first_name', 'last_name', 'phone', 'email']
            for f in required_fields:
                self.fields[f].required = True
        super()._clean_fields()

