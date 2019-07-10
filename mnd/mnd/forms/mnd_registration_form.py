from django.forms import BooleanField, CharField, ChoiceField, IntegerField
from django.utils.translation import gettext as _

from rdrf.forms.registration_forms import PatientRegistrationForm

from mnd.utils import load_insurers_list
from mnd.constants import CONTACT_METHOD_CHOICES, PLAN_MANAGER_CHOICES, PRIMARY_CARER_RELATIONS


class MNDRegistrationForm(PatientRegistrationForm):

    PatientRegistrationForm.placeholders.update({
        'contact_method': _("Preferred contact method"),
        'contact_email': _("Email address"),
        'contact_first_name': _("Preferred contact first name"),
        'contact_surname': _("Preferred contact family name"),
        'contact_phone': _("Preferred contact phone"),
        'medicare_number': _("Medicare number"),
        'pension_number': _("Pension number"),
        'health_fund_number': _("Private Health fund number"),
        'ndis_number': _("NDIS number"),
        'ndis_coordinator_first_name': _("NDIS case coordinator first name"),
        'ndis_coordinator_surname': _("NDIS case coordinator family name"),
        'ndis_coordinator_phone': _("NDIS case coordinator phone"),
        'primary_carer_first_name': _("Primary carer first name"),
        'primary_carer_surname': _("Primary carer family name"),
        'primary_carer_phone': _("Primary carer phone"),
        'primary_carer_email': _("Primary carer email"),
        'primary_carer_relation_specify': _("Specify relation to primary carer")

    })
    PatientRegistrationForm.no_placeholder_fields.extend(['is_primary_carer'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    contact_email = CharField(required=False, max_length=30)
    contact_method = ChoiceField(choices=CONTACT_METHOD_CHOICES, required=True, initial="")
    contact_first_name = CharField(required=False, max_length=30)
    contact_surname = CharField(required=False, max_length=30)
    contact_phone = CharField(required=False, max_length=30)
    is_primary_carer = BooleanField(required=False)
    medicare_number = IntegerField(required=False)
    pension_number = IntegerField(required=False)
    insurer = ChoiceField(choices=load_insurers_list(), required=False)
    health_fund_number = IntegerField(required=False)
    ndis_number = IntegerField(required=False)
    ndis_plan_manager = ChoiceField(choices=PLAN_MANAGER_CHOICES, required=False)
    ndis_coordinator_first_name = CharField(required=False, max_length=30)
    ndis_coordinator_surname = CharField(required=False, max_length=30)
    ndis_coordinator_phone = CharField(required=False, max_length=30)
    primary_carer_first_name = CharField(required=False, max_length=30)
    primary_carer_surname = CharField(required=False, max_length=30)
    primary_carer_phone = CharField(required=False, max_length=30)
    primary_carer_email = CharField(required=False, max_length=30)
    primary_carer_relationship = ChoiceField(choices=PRIMARY_CARER_RELATIONS, required=False)
    primary_carer_relation_specify = CharField(required=False, max_length=30)

    def _clean_fields(self):
        if self.data.get('insurer', '').strip() != '':
            self.fields['health_fund_number'].required = True
        if self.data.get('ndis_number','').strip() != '':
            self.fields['ndis_plan_manager'].required = True
            if self.data.get('ndis_plan_manager', '').strip() == 'other':
                for f in ['ndis_coordinator_first_name', 'ndis_coordinator_surname', 'ndis_coordinator_phone']:
                    self.fields[f].required = True
        super()._clean_fields()