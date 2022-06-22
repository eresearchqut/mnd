import logging

import graphene
from graphene_django import DjangoObjectType
from mnd.models import PrimaryCarer
from mnd.models import PrimaryCarerRelationship, PreferredContact, PatientInsurance
from report.schema import get_patient_fields

logger = logging.getLogger(__name__)


class PreferredContactType(DjangoObjectType):
    class Meta:
        model = PreferredContact


class PrimaryCarerType(DjangoObjectType):
    class Meta:
        model = PrimaryCarer


class InsuranceDataType(DjangoObjectType):
    ndis_plan_manager = graphene.String()
    needed_mac_level = graphene.String()
    home_care_level = graphene.String()

    class Meta:
        model = PatientInsurance

    def resolve_ndis_plan_manager(self, info):
        return self.ndis_plan_manager

    def resolve_needed_mac_level(self, info):
        return self.needed_mac_level

    def resolve_home_care_level(self, info):
        return self.home_care_level


def get_mnd_patient_fields():

    def resolve_primary_carer_relationship(patient, info):
        primary_carer = patient.primary_carers.first()
        return PrimaryCarerRelationship.objects.filter(carer=primary_carer, patient=patient).first().relationship

    patient_fields = get_patient_fields()

    patient_fields['Meta'].fields.extend(['preferred_contact', 'insurance_data'])
    patient_fields.update({
        "is_duplicate_patient": graphene.String(),
        "resolve_is_duplicate_patient":
            lambda patient, info: hasattr(patient, "duplicate_patient") and patient.duplicate_patient.is_duplicate,
        "primary_carer": graphene.Field(PrimaryCarerType),
        "resolve_primary_carer": lambda patient, info: patient.primary_carers.first(),
        "primary_carer_relationship": graphene.String(),
        "resolve_primary_carer_relationship": resolve_primary_carer_relationship
    })

    return patient_fields
