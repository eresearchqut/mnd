import pycountry

from django.db import models

from django.utils.translation import gettext as _
from django.utils import timezone
from registry.patients.models import Patient


class PatientInsurance(models.Model):

    PLAN_MANAGER_CHOICES = [
        ('', _("NDIS Plan Manager")),
        ('self', _("Self")),
        ('agency', _("Agency")),
        ('other', _("Other")),
    ]

    DVA_CARD_TYPE_CHOICES = [
        ('', _("DVA card type")),
        ('Gold', _("Gold")),
        ('White', _("White")),
        ('ppbc', _('Repatriation Pharmaceutical Benefits Card'))
    ]

    CARE_LEVEL_CHOICES = [
        ('', _("Care level")),
        ('one', _("One")),
        ('two', _("Two")),
        ('three', _("Three")),
        ('four', _("Four"))
    ]

    patient = models.OneToOneField(Patient, related_name='insurance_data', on_delete=models.CASCADE)
    medicare_number = models.CharField(max_length=30, null=True, blank=True)
    pension_number = models.CharField(max_length=30, null=True, blank=True)
    private_health_fund = models.CharField(max_length=255, null=True, blank=True)
    private_health_fund_number = models.CharField(max_length=30, null=True, blank=True)
    ndis_number = models.CharField(max_length=30, null=True, blank=True)
    ndis_plan_manager = models.CharField(choices=PLAN_MANAGER_CHOICES, max_length=30)
    ndis_coordinator_first_name = models.CharField(max_length=30, null=True, blank=True)
    ndis_coordinator_last_name = models.CharField(max_length=30, null=True, blank=True)
    ndis_coordinator_phone = models.CharField(max_length=30, null=True, blank=True)
    ndis_coordinator_email = models.CharField(max_length=30, null=True, blank=True)
    dva_card_number = models.CharField(max_length=30, null=True, blank=True)
    dva_card_type = models.CharField(choices=DVA_CARD_TYPE_CHOICES, max_length=30, default='')
    referred_for_mac_care = models.BooleanField(blank=True, null=True)
    needed_mac_level = models.CharField(choices=CARE_LEVEL_CHOICES, max_length=30, default='')
    eligible_for_home_care = models.BooleanField(blank=False, null=False, default=False)
    receiving_home_care = models.BooleanField(blank=False, null=False, default=False)
    home_care_level = models.CharField(choices=CARE_LEVEL_CHOICES, max_length=30, default='')


class PrimaryCarer(models.Model):

    @classmethod
    def get_primary_carer(cls, patient):
        return patient.primary_carers.first()

    LANGUAGE_CHOICES = [
        (l.alpha_2, l.name) for l in pycountry.languages if hasattr(l, 'alpha_2')
    ]

    patients = models.ManyToManyField(Patient, related_name='primary_carers')
    # This is Many to Many as we don't want to add a FK to Patient in TRRF
    # since TRRF is not aware of this MND specific model
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    preferred_language = models.CharField(choices=LANGUAGE_CHOICES, max_length=30, default='en')
    interpreter_required = models.BooleanField(null=False, blank=False, default=False)
    same_address = models.BooleanField(null=False, blank=False, default=True)
    suburb = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class PrimaryCarerRelationship(models.Model):

    PRIMARY_CARER_RELATIONS = [
        ('', _("Primary carer relationship")),
        ('spouse', _("Spouse")),
        ('child', _("Child")),
        ('sibling', _("Sibling")),
        ('friend', _("Friend")),
        ('other', _("Other(specify)")),
    ]
    carer = models.ForeignKey(PrimaryCarer, related_name='relation', on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, related_name='carer_relation', on_delete=models.CASCADE)
    relationship = models.CharField(choices=PRIMARY_CARER_RELATIONS, max_length=30)
    relationship_info = models.CharField(max_length=30, null=True, blank=True)


class PreferredContact(models.Model):

    CONTACT_METHOD_CHOICES = [
        ('', _("Preferred contact method")),
        ('phone', _("Phone")),
        ('sms', _("SMS")),
        ('email', _("Email")),
        ('primary_carer', _("Primary Carer")),
        ('person', _("Nominated person below")),
    ]

    patient = models.OneToOneField(Patient, related_name='preferred_contact', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.CharField(max_length=30, null=True, blank=True)
    contact_method = models.CharField(choices=CONTACT_METHOD_CHOICES, max_length=30)


class CarerRegistrationManager(models.Manager):

    def has_pending_registration(self, primary_carer):
        return self.filter(
            carer=primary_carer, expires_on__gte=timezone.now(), status=CarerRegistration.CREATED
        ).exists()

    def has_registered_carer(self, primary_carer, patient):
        return self.filter(
            carer=primary_carer, patient=patient, status=CarerRegistration.REGISTERED
        ).exists()

    def has_deactivated_carer(self, primary_carer, patient):
        return self.filter(
            carer=primary_carer, patient=patient, status=CarerRegistration.DEACTIVATED
        ).exists()

    def has_expired_registration(self, primary_carer):
        return self.filter(
            carer=primary_carer, expires_on__lt=timezone.now(), status=CarerRegistration.CREATED,
        ).exists()


class CarerRegistration(models.Model):

    CREATED = 'created'
    REGISTERED = 'registered'
    DEACTIVATED = 'deactivated'

    REGISTRATION_STATUS_CHOICES = [
        (CREATED, CREATED),
        (REGISTERED, REGISTERED),
        (DEACTIVATED, DEACTIVATED),
    ]
    carer = models.ForeignKey(PrimaryCarer, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    token = models.UUIDField()
    status = models.CharField(
        choices=REGISTRATION_STATUS_CHOICES,
        null=False,
        blank=False,
        default=CREATED,
        max_length=16
    )
    expires_on = models.DateTimeField()
    registration_ts = models.DateTimeField(null=True, blank=True)

    objects = CarerRegistrationManager()
