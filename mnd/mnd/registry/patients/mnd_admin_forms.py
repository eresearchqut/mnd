import logging

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils import timezone

from registry.groups.models import CustomUser
from registry.patients.models import Patient

from mnd.models import (
    CarerRegistration,
    PreferredContact,
    PatientInsurance,
    PrimaryCarer,
    PrimaryCarerRelationship,
)


logger = logging.getLogger(__name__)


class PrefixedModelForm(forms.ModelForm):

    def field_name(self, name):
        return f"{self.prefix}-{name}" if self.prefix else name


class PatientInsuranceForm(PrefixedModelForm):

    _NULLABLE_BOOL_FIELD_YES = "2"

    class Meta:
        model = PatientInsurance
        fields = (
            'medicare_number', 'pension_number', 'private_health_fund', 'private_health_fund_number',
            'ndis_number', 'ndis_plan_manager', 'ndis_coordinator_first_name',
            'ndis_coordinator_last_name', 'ndis_coordinator_phone', 'ndis_coordinator_email',
            'dva_card_number', 'dva_card_type', 'referred_for_mac_care',
            'needed_mac_level', 'eligible_for_home_care', 'receiving_home_care', 'home_care_level'
        )
        labels = {
            'ndis_number': _('NDIS number'),
            'ndis_plan_manager': _('NDIS Plan Manager'),
            'ndis_coordinator_first_name': _('NDIS Coordinator first name'),
            'ndis_coordinator_last_name': _('NDIS Coordinator last name'),
            'ndis_coordinator_phone': _('NDIS Coordinator phone'),
            'ndis_coordinator_email': _('NDIS Coordinator email'),
            'dva_card_number': _("DVA card number"),
            'dva_card_type': _("DVA card type"),
            'referred_for_mac_care': _("Have you been referred for aged care via My Aged Care (MAC)?"),
            'needed_mac_level': _("What MAC level were you assessed as needing?"),
            'eligible_for_home_care': _("Eligible for a Community home care package?"),
            'receiving_home_care': _("Are you receiving a community home care package?"),
            'home_care_level': _("Home care package level")
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


class PrimaryCarerForm(PrefixedModelForm):

    relationship = forms.ChoiceField(
        choices=PrimaryCarerRelationship.PRIMARY_CARER_RELATIONS, required=True,
        widget=forms.widgets.RadioSelect
    )
    relationship_info = forms.CharField(max_length=30, required=False)
    interpreter_required = forms.BooleanField(
        widget=forms.widgets.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patient = None

    @staticmethod
    def _is_valid_phone(phone_no):
        return phone_no and all(c.isdigit() for c in phone_no)

    class Meta:
        model = PrimaryCarer
        fields = (
            'first_name', 'last_name', 'phone', 'email', 'relationship', 'relationship_info',
            'preferred_language', 'interpreter_required', 'same_address', 'address',
            'suburb', 'postcode', 'is_emergency_contact', 'em_contact_first_name',
            'em_contact_last_name', 'em_contact_phone'
        )
        labels = {
            'is_emergency_contact': _('Is the primary carer the emergency contact number'),
            'em_contact_first_name': _('Emergency contact first name'),
            'em_contact_last_name': _('Emergency contact last name'),
            'em_contact_phone': _('Emergency contact phone'),
        }

    def _clean_fields(self):
        required_relationship_info = self.data.get(self.field_name('relationship'), '') == 'other'
        self.fields['relationship_info'].required = required_relationship_info
        super()._clean_fields()

    def has_assigned_carer(self):
        instance = getattr(self, 'instance')
        if instance and self.patient:
            return CarerRegistration.objects.has_registered_carer(instance, self.patient)
        return False

    def set_patient(self, patient):
        self.patient = patient
        if self.has_assigned_carer():
            for f in self.fields:
                if f not in ('relationship', 'relationship_info'):
                    self.fields[f].widget.attrs['readonly'] = True
            notification = (
                _("""You can't change the personal details of the principal caregiver while it is linked.
                     To unlink the principal caregiver please use the Carer Management menu!""")
            )
            self.fields['first_name'].help_text = mark_safe(f"<span style=\"color:green;\"><strong>{notification} </strong></span>")

    def clean_em_contact_phone(self):
        em_contact_phone = self.cleaned_data['em_contact_phone']
        if not self._is_valid_phone(em_contact_phone):
            raise forms.ValidationError(_("The emergency contact phone should contain digits only"))

    def clean__phone(self):
        phone = self.cleaned_data['phone']
        if not self._is_valid_phone(phone):
            raise forms.ValidationError(_("The phone number should contain digits only"))

    def clean_email(self):
        email = self.cleaned_data['email']
        instance = getattr(self, 'instance', None)

        existing_user = CustomUser.objects.filter(username__iexact=email.lower(), is_active=True).first()
        if existing_user and not existing_user.is_carer:
            raise forms.ValidationError(_("The email address is already registered into the system"))

        if Patient.objects.really_all().filter(email=email).exists():
            # Patient with the same email exists. Allow the change here but invites will not be sent out
            return email

        if instance and instance.pk:
            if email != instance.email:
                # Delete pending carer invites for the old email
                CarerRegistration.objects.filter(
                    carer_email=instance.email,
                    status=CarerRegistration.CREATED,
                    expires_on__gte=timezone.now()
                ).delete()
        return email

    def clean(self):
        # To bypass validate_unique on the model
        # in case the user enters an existing email address
        pass

    def save(self, commit=True):
        rel = self.cleaned_data.get('relationship')
        rel_info = self.cleaned_data.get('relationship_info')
        email = self.cleaned_data.get('email')
        instance = getattr(self, 'instance', None)
        carer_instance_update = False
        if 'email' in self.changed_data:
            existing_carer = PrimaryCarer.objects.filter(email__iexact=email.lower()).first()
            if existing_carer:
                carer_instance_update = True
                self.instance = existing_carer
            elif instance:
                # if email is changed and does not point to
                # an existing carer then force creation of a new entry
                self.instance.pk = None

        ret_val = super().save(commit)
        carer = ret_val if carer_instance_update else (self.instance or ret_val)
        if self.patient and commit:
            # There can be only 1 carer per patient from the patient's perspective
            pc, __ = PrimaryCarerRelationship.objects.get_or_create(patient=self.patient)
            pc.carer = carer
            pc.relationship = rel
            pc.relationship_info = rel_info
            pc.save()
        return ret_val


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
