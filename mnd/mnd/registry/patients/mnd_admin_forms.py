from django import forms
from django.utils.translation import ugettext as _

from mnd.models import PatientInsurance, PrimaryCarer, PreferredContact


class PrefixedModelForm(forms.ModelForm):

    def field_name(self, name):
        return f"{self.prefix}-{name}" if self.prefix else name


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
        health_fund_set = self.data.get(self.field_name('private_health_fund'), '') != ''
        self.fields['private_health_fund'].required = health_fund_set
        self.fields['private_health_fund_number'].required = health_fund_set
        self.fields['pension_number'].required = not health_fund_set
        ndis_number_set = self.data.get(self.field_name('ndis_number'), '') != ''
        self.fields['ndis_plan_manager'].required = ndis_number_set
        ndis_coordinator_info = [
            'ndis_coordinator_first_name', 'ndis_coordinator_last_name', 'ndis_coordinator_phone'
        ]
        coordinator_required_data = self.data.get(self.field_name('ndis_plan_manager'), '') == 'other'
        for f in ndis_coordinator_info:
            self.fields[f].required = coordinator_required_data and ndis_number_set
        super()._clean_fields()


class PrimaryCarerForm(PrefixedModelForm):

    class Meta:
        model = PrimaryCarer
        fields = ('first_name', 'last_name', 'phone', 'email', 'relationship', 'relationship_info')

    def _clean_fields(self):
        required_relationship_info = self.data.get(self.field_name('relationship'), '') == 'other'
        self.fields['relationship_info'].required = required_relationship_info
        super()._clean_fields()


class PreferredContactForm(PrefixedModelForm):
    class Meta:
        model = PreferredContact
        fields = ('contact_method', 'first_name', 'last_name', 'phone', 'email')

    def _clean_fields(self):
        required_info = self.data.get(self.field_name('contact_method'), '') == 'person'
        if required_info:
            required_fields = ['first_name', 'last_name', 'phone', 'email']
            for f in required_fields:
                self.fields[f].required = True
        super()._clean_fields()

