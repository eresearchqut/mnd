from django.db import models

from registry.patients.models import Patient

from .constants import PRIMARY_CARER_RELATIONS, CONTACT_METHOD_CHOICES, PLAN_MANAGER_CHOICES
from .utils import load_insurers_list


class PatientInsurance(models.Model):
    patient = models.OneToOneField(Patient, related_name='insurance_data', on_delete=models.CASCADE)
    medicare_number = models.BigIntegerField(null=True, blank=True)
    pension_number = models.BigIntegerField(null=True, blank=True)
    private_health_fund_name = models.CharField(choices=load_insurers_list(), max_length=10, blank=True)
    private_health_fund_number = models.BigIntegerField(null=True, blank=True)
    ndis_number = models.CharField(max_length=30)
    ndis_plan_manager = models.CharField(choices=PLAN_MANAGER_CHOICES, max_length=30)
    ndis_coordinator_first_name = models.CharField(max_length=30, null=True, blank=True)
    ndis_coordinator_last_name = models.CharField(max_length=30, null=True, blank=True)
    ndis_coordinator_phone = models.CharField(max_length=30, null=True, blank=True)


class PrimaryCarer(models.Model):
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
    patient = models.OneToOneField(Patient, related_name='preferred_contact', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    primary_carer = models.OneToOneField(PrimaryCarer, related_name='preferred_contact', on_delete=models.CASCADE,
                                         null=True, blank=True)
    contact_method = models.CharField(choices=CONTACT_METHOD_CHOICES, max_length=30)





