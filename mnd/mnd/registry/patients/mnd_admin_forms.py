import logging

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils import timezone

from rdrf.events.events import EventType
from rdrf.services.io.notifications.email_notification import process_notification
from registry.groups.models import CustomUser
from registry.patients.models import Patient

from rdrf.forms.widgets import widgets

from mnd.models import (
    CarerRegistration,
    PreferredContact,
    PatientInsurance,
    PrimaryCarer,
    PrimaryCarerRelationship,
    DuplicatePatient,
)


logger = logging.getLogger(__name__)


class PrefixedModelForm(forms.ModelForm):

    def field_name(self, name):
        return f"{self.prefix}-{name}" if self.prefix else name


class PatientInsuranceForm(PrefixedModelForm):

    has_private_health_fund = forms.BooleanField(widget=widgets.RadioSelect(
        choices=[(True, 'Yes'), (False, 'No')]),
        required=False,
        label=_('Do you have a private health fund?')
    )
    is_ndis_participant = forms.BooleanField(
        widget=widgets.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        required=False,
        label=_('Are you currently an NDIS participant?')
    )
    is_ndis_eligible = forms.BooleanField(widget=widgets.RadioSelect(
        choices=[(True, 'Yes'), (False, 'No')]),
        required=False,
        label=_('Are you eligible for the NDIS (under 65)?')
    )
    has_dva_card = forms.BooleanField(
        widget=widgets.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        required=False,
        label=_("Do you have a DVA card?")
    )
    ndis_plan_manager = forms.ChoiceField(
        choices=PatientInsurance.PLAN_MANAGER_CHOICES, required=False,
        widget=widgets.RadioSelect,
        label=_('NDIS Plan Manager')
    )
    dva_card_type = forms.ChoiceField(
        choices=PatientInsurance.DVA_CARD_TYPE_CHOICES, required=False,
        widget=widgets.RadioSelect,
        label=_("DVA card type"),
    )
    referred_for_mac_care = forms.BooleanField(
        widget=widgets.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        required=False,
        label=_("Have you been referred for aged care support services via My Aged Care (MAC)?"),
    )
    needed_mac_level = forms.ChoiceField(
        choices=PatientInsurance.CARE_LEVEL_CHOICES,
        widget=widgets.RadioSelect,
        label=_("What MAC level were you assessed as needing?")
    )
    home_care_level = forms.ChoiceField(
        choices=PatientInsurance.CARE_LEVEL_CHOICES,
        widget=widgets.RadioSelect,
        label=_("What level package are you receiving")
    )

    class Meta:
        model = PatientInsurance
        fields = (
            'main_hospital', 'main_hospital_mrn', 'secondary_hospital', 'secondary_hospital_mrn',
            'medicare_number', 'pension_number', 'has_private_health_fund',
            'private_health_fund', 'private_health_fund_number', 'is_ndis_participant',
            'is_ndis_eligible', 'ndis_number', 'ndis_plan_manager', 'ndis_coordinator_first_name',
            'ndis_coordinator_last_name', 'ndis_coordinator_phone', 'ndis_coordinator_email',
            'has_dva_card', 'dva_card_number', 'dva_card_type', 'referred_for_mac_care',
            'needed_mac_level', 'eligible_for_home_care', 'receiving_home_care', 'home_care_level',
        )
        labels = {
            'private_health_fund': _('Name of Private Health fund'),
            'private_health_fund_number': _('Private Health Fund number'),
            'ndis_number': _('NDIS number'),
            'ndis_coordinator_first_name': _('NDIS support coordinator first name'),
            'ndis_coordinator_last_name': _('NDIS support coordinator last name'),
            'ndis_coordinator_phone': _('NDIS support coordinator phone'),
            'ndis_coordinator_email': _('NDIS support coordinator email'),
            'dva_card_number': _("DVA card number"),
            'eligible_for_home_care': _("Have you been assessed as being eligible for a community home care package?"),
            'receiving_home_care': _("Are you receiving a community home care package?"),
            'main_hospital': _("Main Hospital attended for MND"),
            'main_hospital_mrn': _("Medical record number (MRN)"),
            'secondary_hospital': _("Secondary Hospital/Health Service"),
            'secondary_hospital_mrn': _("Medical record number (MRN)"),
        }

    def clean_ndis_number(self):
        ndis_number = self.cleaned_data['ndis_number']
        digits_only = ndis_number and all(c.isdigit() for c in ndis_number)
        if ndis_number and (not digits_only or len(ndis_number) != 10):
            raise forms.ValidationError(_("NDIS number should contain 10 digits"))
        return ndis_number

    def _clean_fields(self):
        radio_yes_value = 'True'
        has_private_health_fund = self.data.get(self.field_name('has_private_health_fund'), '') == radio_yes_value
        self.fields['private_health_fund'].required = has_private_health_fund
        self.fields['private_health_fund_number'].required = has_private_health_fund
        is_ndis_participant = self.data.get(self.field_name('is_ndis_participant'), '') == radio_yes_value
        self.fields['ndis_number'].required = is_ndis_participant
        self.fields['ndis_plan_manager'].required = is_ndis_participant
        ndis_coordinator_info = [
            'ndis_coordinator_first_name', 'ndis_coordinator_last_name', 'ndis_coordinator_phone',
            'ndis_coordinator_email'
        ]
        coordinator_required_data = self.data.get(self.field_name('ndis_plan_manager'), '') == 'other'
        for f in ndis_coordinator_info:
            self.fields[f].required = coordinator_required_data and is_ndis_participant
        has_dva_card = self.data.get(self.field_name('has_dva_card'), '') == radio_yes_value
        self.fields['dva_card_number'].required = has_dva_card
        self.fields['dva_card_type'].required = has_dva_card
        referred_for_mac_care_set = self.data.get(self.field_name('referred_for_mac_care'), '') == radio_yes_value
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
        widget=widgets.RadioSelect
    )
    relationship_info = forms.CharField(max_length=30, required=False)
    interpreter_required = forms.BooleanField(
        widget=widgets.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patient = None

    @staticmethod
    def _is_valid_phone(phone_no):
        return not phone_no or (phone_no and all(c.isdigit() for c in phone_no))

    class Meta:
        model = PrimaryCarer
        fields = (
            'first_name', 'last_name', 'phone', 'email', 'relationship', 'relationship_info',
            'interpreter_required', 'preferred_language', 'same_address', 'address',
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
        interpreter_required = self.data.get(self.field_name('interpreter_required'), '') == 'True'
        self.fields['preferred_language'].required = interpreter_required
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
        return em_contact_phone

    def clean__phone(self):
        phone = self.cleaned_data['phone']
        if not self._is_valid_phone(phone):
            raise forms.ValidationError(_("The phone number should contain digits only"))
        return phone

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
    contact_method = forms.ChoiceField(
        choices=PreferredContact.CONTACT_METHOD_CHOICES, required=True,
        widget=widgets.RadioSelect
    )

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


class DuplicatePatientForm(PrefixedModelForm):
    is_duplicate = forms.BooleanField(label=_("Mark this patient as a potential duplicate"), required=False)

    class Meta:
        model = DuplicatePatient
        fields = ('is_duplicate',)

    def save(self, commit=True):
        if 'is_duplicate' in self.changed_data and self.cleaned_data['is_duplicate']:
            patient = self.instance.patient
            registry_code = patient.rdrf_registry.first().code
            process_notification(registry_code, EventType.DUPLICATE_PATIENT_SET,
                                 {"patient": patient})

        return super().save(commit)
