import pycountry

from django.contrib.postgres.fields import ArrayField
from django.db import models

from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from registry.patients.models import Patient

LANGUAGE_CHOICES = [
    (lang.alpha_2, lang.name) for lang in pycountry.languages if hasattr(lang, 'alpha_2')
]


class PatientInsurance(models.Model):

    PLAN_MANAGER_CHOICES = [
        ('self', _("Self")),
        ('agency', _("Agency")),
        ('other', _("Other")),
    ]

    DVA_CARD_TYPE_CHOICES = [
        ('', _("N/A")),
        ('Gold', _("Gold")),
        ('White', _("White")),
        ('ppbc', _("RPB"))
    ]

    CARE_LEVEL_CHOICES = [
        ('one', _("One")),
        ('two', _("Two")),
        ('three', _("Three")),
        ('four', _("Four"))
    ]

    patient = models.OneToOneField(Patient, related_name='insurance_data', on_delete=models.CASCADE)
    medicare_number = models.CharField(max_length=30, null=True, blank=True)
    pension_number = models.CharField(max_length=30, null=True, blank=True)
    has_private_health_fund = models.BooleanField(blank=False, null=False, default=False)
    private_health_fund = models.CharField(max_length=255, null=True, blank=True)
    private_health_fund_number = models.CharField(max_length=30, null=True, blank=True)
    is_ndis_participant = models.BooleanField(blank=False, null=False, default=False, verbose_name=_("Are you currently an NDIS participant?"))
    ndis_number = models.CharField(max_length=30, verbose_name=_('NDIS number'), null=True, blank=True, help_text=_('10 digits'))
    is_ndis_eligible = models.BooleanField(blank=False, null=False, default=False, verbose_name=_("Are you eligible for the NDIS (under 65)?"))
    ndis_plan_manager = models.CharField(choices=PLAN_MANAGER_CHOICES, verbose_name=_('NDIS plan manager'), max_length=30)
    ndis_coordinator_first_name = models.CharField(max_length=30, verbose_name=_('NDIS coordinator first name'), null=True, blank=True)
    ndis_coordinator_last_name = models.CharField(max_length=30, verbose_name=_('NDIS coordinator last name'), null=True, blank=True)
    ndis_coordinator_phone = models.CharField(max_length=30, verbose_name=_('NDIS coordinator phone'), null=True, blank=True)
    ndis_coordinator_email = models.CharField(max_length=30, verbose_name=_('NDIS coordinator email'), null=True, blank=True)
    has_dva_card = models.BooleanField(blank=False, null=False, default=False, verbose_name=_('Do you have a DVA card?'))
    dva_card_number = models.CharField(max_length=30, verbose_name=_('DVA card number'), null=True, blank=True)
    dva_card_type = models.CharField(choices=DVA_CARD_TYPE_CHOICES, verbose_name=_('DVA card type'), max_length=30, default='')
    referred_for_mac_care = models.BooleanField(verbose_name=_('Referral for My Aged Care (MAC)'), blank=True, null=True)
    needed_mac_level = models.CharField(choices=CARE_LEVEL_CHOICES, verbose_name=_('Needed My Aged Care (MAC) level'), max_length=30, default='')
    eligible_for_home_care = models.BooleanField(blank=False, null=False, default=False)
    receiving_home_care = models.BooleanField(blank=False, null=False, default=False)
    home_care_level = models.CharField(choices=CARE_LEVEL_CHOICES, max_length=30, default='')
    main_hospital = models.CharField(max_length=255, null=True, blank=True)
    main_hospital_mrn = models.CharField(max_length=32, null=True, blank=True, help_text=_('At your main hospital attended for MND, if known'))
    secondary_hospital = models.CharField(max_length=255, null=True, blank=True)
    secondary_hospital_mrn = models.CharField(max_length=32, null=True, blank=True, help_text=_('At your secondary hospital / health service  if known'))


class PrimaryCarer(models.Model):

    @classmethod
    def get_primary_carer(cls, patient):
        return patient.primary_carers.first() if patient else None

    # This is Many to Many as we don't want to add a FK to Patient in TRRF
    # since TRRF is not aware of this MND specific model
    patients = models.ManyToManyField(Patient, related_name='primary_carers', through='PrimaryCarerRelationship')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    mobile_phone = models.CharField(max_length=30)
    home_phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=30, unique=True)
    preferred_language = models.CharField(choices=LANGUAGE_CHOICES, max_length=30, default='en')
    interpreter_required = models.BooleanField(default=False)
    same_address = models.BooleanField(default=True)
    suburb = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    is_emergency_contact = models.BooleanField(default=False)
    em_contact_first_name = models.CharField(max_length=30, null=True, blank=True)
    em_contact_last_name = models.CharField(max_length=30, null=True, blank=True)
    em_contact_phone = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def clean(self):
        if self.email:
            self.email = self.email.lower()


class PrimaryCarerRelationship(models.Model):

    PRIMARY_CARER_RELATIONS = [
        ('', _("None")),
        ('spouse', _("Spouse")),
        ('child', _("Child")),
        ('sibling', _("Sibling")),
        ('friend', _("Friend")),
        ('other', _("Other(specify)")),
    ]
    carer = models.ForeignKey(PrimaryCarer, related_name='relation', on_delete=models.CASCADE)
    patient = models.OneToOneField(Patient, related_name='carer_relation', on_delete=models.CASCADE)
    relationship = models.CharField(choices=PRIMARY_CARER_RELATIONS, max_length=30)
    relationship_info = models.CharField(max_length=30, null=True, blank=True)


class PreferredContact(models.Model):

    CONTACT_METHOD_CHOICES = [
        ('phone', _("Phone")),
        ('sms', _("SMS")),
        ('email', _("Email")),
        ('primary_carer', _("Phone my Principal Caregiver")),
        ('emergency_contact', _("Phone my Emergency Contact")),
        ('person', _("Nominated person below")),
    ]

    patient = models.OneToOneField(Patient, related_name='preferred_contact', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.CharField(max_length=30, null=True, blank=True)
    contact_method = models.CharField(choices=CONTACT_METHOD_CHOICES, max_length=30)


class CarerRegistrationManager(models.Manager):

    def _pending_registration_qs(self, primary_carer, patient):
        return self.filter(
            carer=primary_carer,
            carer_email=primary_carer.email,
            patient=patient,
            expires_on__gte=timezone.now(),
            status=CarerRegistration.CREATED
        )

    def get_pending_registration(self, primary_carer, patient):
        return self._pending_registration_qs(primary_carer, patient).first()

    def has_pending_registration(self, primary_carer, patient):
        return self._pending_registration_qs(primary_carer, patient).exists()

    def is_carer_registered(self, primary_carer, patient):
        return self.filter(
            carer=primary_carer,
            carer_email=primary_carer.email,
            patient=patient,
            status=CarerRegistration.REGISTERED
        ).exists()

    def has_registered_carer(self, primary_carer, patient):
        return self.filter(
            carer=primary_carer,
            patient=patient,
            carer_email=primary_carer.email,
            status=CarerRegistration.REGISTERED
        ).exists()

    def has_deactivated_carer(self, primary_carer, patient):
        return self.filter(
            carer=primary_carer,
            patient=patient,
            carer_email=primary_carer.email,
            status=CarerRegistration.DEACTIVATED
        ).exists()

    def has_expired_registration(self, primary_carer, patient):
        last_registration = self.filter(
            carer=primary_carer,
            patient=patient,
            carer_email=primary_carer.email,
            status=CarerRegistration.CREATED
        ).order_by('-expires_on').first()
        return last_registration is not None and last_registration.expires_on < timezone.now()

    def has_registration_records(self, primary_carer, patient):
        pending = self.has_pending_registration(primary_carer)
        registered = self.has_registered_carer(primary_carer, patient)
        deactivated = self.has_deactivated_carer(primary_carer, patient)
        return pending or deactivated or registered


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
    carer_email = models.EmailField(max_length=30, default="unset@email.com")
    token = models.UUIDField()
    status = models.CharField(choices=REGISTRATION_STATUS_CHOICES, default=CREATED, max_length=16)
    expires_on = models.DateTimeField()
    registration_ts = models.DateTimeField(null=True, blank=True)

    objects = CarerRegistrationManager()


class DuplicatePatient(models.Model):
    patient = models.OneToOneField(Patient, related_name='duplicate_patient', on_delete=models.CASCADE)
    is_duplicate = models.BooleanField(blank=False, null=False, default=False)


class PatientLanguage(models.Model):
    patient = models.OneToOneField(Patient, related_name='language_info', on_delete=models.CASCADE)
    preferred_language = models.CharField(choices=LANGUAGE_CHOICES, max_length=30, default='en')
    interpreter_required = models.BooleanField(default=False)


class MIMSSearchTerm(models.Model):
    search_term = models.CharField(max_length=32, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField()
    products = ArrayField(models.UUIDField(), blank=True)


class MIMSProductCache(models.Model):

    product_id = models.UUIDField(unique=True)
    name = models.CharField(max_length=256)
    active_ingredient = models.TextField()
    mims_classes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]


class MIMSCmiCache(models.Model):
    product_id = models.UUIDField(unique=True)
    product_name = models.CharField(max_length=256, null=True, blank=True)
    cmi_id = models.UUIDField(null=True, blank=True)
    cmi_link = models.CharField(max_length=512)
    has_link = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_on = models.DateTimeField()
