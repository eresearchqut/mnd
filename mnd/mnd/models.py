from django.db import models

from django.utils.translation import gettext as _
from registry.patients.models import Patient


class PrivateHealthFund(models.Model):
    code = models.CharField(max_length=15)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=15)
    parent = models.ForeignKey('self', related_name='+', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PatientInsurance(models.Model):

    PLAN_MANAGER_CHOICES = [
        ('', _("NDIS Plan Manager")),
        ('self', _("Self")),
        ('agency', _("Agency")),
        ('other', _("Other")),
    ]

    patient = models.OneToOneField(Patient, related_name='insurance_data', on_delete=models.CASCADE)
    medicare_number = models.CharField(max_length=30, null=True, blank=True)
    pension_number = models.CharField(max_length=30, null=True, blank=True)
    private_health_fund = models.ForeignKey(PrivateHealthFund, null=True, blank=True, on_delete=models.CASCADE)
    private_health_fund_number = models.CharField(max_length=30, null=True, blank=True)
    ndis_number = models.CharField(max_length=30, null=True, blank=True)
    ndis_plan_manager = models.CharField(choices=PLAN_MANAGER_CHOICES, max_length=30)
    ndis_coordinator_first_name = models.CharField(max_length=30, null=True, blank=True)
    ndis_coordinator_last_name = models.CharField(max_length=30, null=True, blank=True)
    ndis_coordinator_phone = models.CharField(max_length=30, null=True, blank=True)


class PrimaryCarer(models.Model):

    PRIMARY_CARER_RELATIONS = [
        ('', _("Primary carer relationship")),
        ('spouse', _("Spouse")),
        ('child', _("Child")),
        ('sibling', _("Sibling")),
        ('friend', _("Friend")),
        ('other', _("Other(specify)")),
    ]

    patient = models.OneToOneField(Patient, related_name='primary_carer', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    relationship = models.CharField(choices=PRIMARY_CARER_RELATIONS, max_length=30)
    relationship_info = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


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





