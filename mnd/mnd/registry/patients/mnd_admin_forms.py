from django import forms
from mnd.models import PatientInsurance, PrimaryCarer, PreferredContact


class PatientInsuranceForm(forms.ModelForm):
    class Meta:
        model = PatientInsurance
        fields = ('medicare_number', 'pension_number', 'private_health_fund_name', 'private_health_fund_number',
                  'ndis_number', 'ndis_plan_manager', 'ndis_coordinator_first_name',
                  'ndis_coordinator_last_name', 'ndis_coordinator_phone')

    def _clean_fields(self):
        health_fund_number_set = self.data.get('private_health_fund_name', '').strip() != ''
        self.fields['private_health_fund_number'].required = health_fund_number_set
        self.fields['pension_number'].required = not health_fund_number_set
        ndis_number_set = self.data.get('ndis_number', '').strip() != ''
        self.fields['private_health_fund_name'].required = not ndis_number_set
        self.fields['private_health_fund_number'].required = not ndis_number_set
        ndis_coordinator_info = [
            'ndis_coordinator_first_name', 'ndis_coordinator_last_name', 'ndis_coordinator_phone'
        ]
        coordinator_required_data = self.data.get('ndis_plan_manager', '').strip() == 'other'
        for f in ndis_coordinator_info:
            self.fields[f].required = coordinator_required_data
        super()._clean_fields()


class PrimaryCarerForm(forms.ModelForm):
    class Meta:
        model = PrimaryCarer
        fields = ('first_name', 'last_name', 'phone', 'email', 'relationship', 'relationship_info')

    def _clean_fields(self):
        required_relationship_info = self.data.get('relationship', '').strip() == 'other'
        self.fields['relationship_info'].required = required_relationship_info


class PreferredContactForm(forms.ModelForm):
    class Meta:
        model = PreferredContact
        fields = ('first_name', 'last_name', 'phone', 'email', 'contact_method')

        def _clean_fields(self):
            required_info = self.data.get('contact_method', '').strip() == 'person'
            if required_info:
                required_fields = ['first_name', 'last_name', 'phone', 'email']
                for f in required_fields:
                    self.fields[f].required = True

