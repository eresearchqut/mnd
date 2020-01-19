from django import forms
from django.utils.translation import ugettext as _

from mnd.models import (
    CarerRegistration,
    PreferredContact,
    PatientInsurance,
    PrimaryCarer,
    PrimaryCarerRelationship,
)


class PrefixedModelForm(forms.ModelForm):

    def field_name(self, name):
        return f"{self.prefix}-{name}" if self.prefix else name


class PatientInsuranceRegistrationForm(PrefixedModelForm):

    class Meta:
        model = PatientInsurance
        fields = ('medicare_number', 'pension_number', 'private_health_fund', 'private_health_fund_number',
                  'ndis_number', 'ndis_plan_manager', 'ndis_coordinator_first_name',
                  'ndis_coordinator_last_name', 'ndis_coordinator_phone', 'ndis_coordinator_email')
        labels = {
            'ndis_number': _('NDIS number'),
            'ndis_plan_manager': _('NDIS Plan Manager'),
            'ndis_coordinator_first_name': _('NDIS Coordinator first name'),
            'ndis_coordinator_last_name': _('NDIS Coordinator last name'),
            'ndis_coordinator_phone': _('NDIS Coordinator phone'),
            'ndis_coordinator_email': _('NDIS Coordinator email'),
        }

    def _clean_fields(self):
        health_fund_set = self.data.get(self.field_name('private_health_fund'), '') != ''
        self.fields['private_health_fund'].required = health_fund_set
        self.fields['private_health_fund_number'].required = health_fund_set
        ndis_number_set = self.data.get(self.field_name('ndis_number'), '') != ''
        self.fields['ndis_plan_manager'].required = ndis_number_set
        ndis_coordinator_info = [
            'ndis_coordinator_first_name', 'ndis_coordinator_last_name', 'ndis_coordinator_phone',
            'ndis_coordinator_email'
        ]
        coordinator_required_data = self.data.get(self.field_name('ndis_plan_manager'), '') == 'other'
        for f in ndis_coordinator_info:
            self.fields[f].required = coordinator_required_data and ndis_number_set
        super()._clean_fields()


class PatientInsuranceForm(PatientInsuranceRegistrationForm):

    _NULLABLE_BOOL_FIELD_YES = "2"

    class Meta:
        model = PatientInsurance
        fields = PatientInsuranceRegistrationForm.Meta.fields + (
            'dva_card_number', 'dva_card_type', 'referred_for_mac_care',
            'needed_mac_level', 'eligible_for_home_care', 'receiving_home_care', 'home_care_level'
        )
        labels = PatientInsuranceRegistrationForm.Meta.labels.update({
            'dva_card_number': _("DVA card number"),
            'dva_card_type': _("DVA card type"),
            'referred_for_mac_care': _("Have you been referred for aged care via My Aged Care (MAC)?"),
            'needed_mac_level': _("What MAC level were you assessed as needing?"),
            'eligible_for_home_care': _("Eligible for a Community home care package?"),
            'receiving_home_care': _("Are you receiving a community home care package?"),
            'home_care_level': _("Home care package level")
        })

    def _clean_fields(self):
        dva_card_number_set = self.data.get(self.field_name('dva_card_number'), '') != ''
        self.fields['dva_card_type'].required = dva_card_number_set
        referred_for_mac_care_set = self.data.get(self.field_name('referred_for_mac_care'), '') != self._NULLABLE_BOOL_FIELD_YES
        self.fields['needed_mac_level'].required = not referred_for_mac_care_set
        eligible_for_home_care = self.data.get(self.field_name('eligible_for_home_care'), '') == 'on'
        if not eligible_for_home_care:
            self.fields['receiving_home_care'].required = False
            self.fields['home_care_level'].required = False
        receiving_home_care = self.data.get(self.field_name('receiving_home_care'), '') == 'on'
        self.fields['home_care_level'].required = receiving_home_care

        super()._clean_fields()


class PrimaryCarerRegistrationForm(PrefixedModelForm):

    relationship = forms.ChoiceField(choices=PrimaryCarerRelationship.PRIMARY_CARER_RELATIONS, required=True)
    relationship_info = forms.CharField(max_length=30, required=False)

    class Meta:
        model = PrimaryCarer
        fields = ('first_name', 'last_name', 'phone', 'email', 'relationship', 'relationship_info')

    def _clean_fields(self):
        required_relationship_info = self.data.get(self.field_name('relationship'), '') == 'other'
        self.fields['relationship_info'].required = required_relationship_info
        super()._clean_fields()


class PrimaryCarerForm(PrimaryCarerRegistrationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patient = None
        instance = getattr(self, 'instance')
        if instance:
            self.fields['email'].widget.attrs['readonly'] = True

    class Meta:
        model = PrimaryCarer
        fields = PrimaryCarerRegistrationForm.Meta.fields + (
            'preferred_language', 'interpreter_required', 'same_address', 'address', 'suburb', 'postcode'
        )

    def save(self, commit=True):
        rel = self.cleaned_data.get('relationship')
        rel_info = self.cleaned_data.get('relationship_info')
        ret_val = super().save(commit)
        if self.instance and self.patient:
            pc, _ = PrimaryCarerRelationship.objects.get_or_create(carer=self.instance, patient=self.patient)
            pc.relationship = rel
            pc.relationship_info = rel_info
            pc.save()
        return ret_val

    def clean_email(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.email:
            return instance.email
        else:
            return self.cleaned_data['email']


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

