import logging

from report.schema.schema import PatientType
from registry.patients.models import Patient
from mnd.models import PrimaryCarer
import graphene
from graphene_django import DjangoObjectType

from mnd.models import PrimaryCarerRelationship, PreferredContact, PatientInsurance

import logging

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


class MNDPatientType(PatientType):
    is_duplicate_patient = graphene.String()
    primary_carer = graphene.Field(PrimaryCarerType)
    primary_carer_relationship = graphene.String()

    class Meta:
        model = Patient
        fields = ('id', 'consent', 'consent_clinical_trials', 'consent_sent_information',
                  'consent_provided_by_parent_guardian', 'family_name', 'given_names', 'maiden_name', 'umrn',
                  'date_of_birth', 'date_of_death', 'place_of_birth', 'date_of_migration', 'country_of_birth',
                  'ethnic_origin', 'sex', 'home_phone', 'mobile_phone', 'work_phone', 'email', 'next_of_kin_family_name',
                  'next_of_kin_given_names', 'next_of_kin_relationship', 'next_of_kin_address', 'next_of_kin_suburb',
                  'next_of_kin_state', 'next_of_kin_postcode', 'next_of_kin_home_phone', 'next_of_kin_mobile_phone',
                  'next_of_kin_work_phone', 'next_of_kin_email', 'next_of_kin_parent_place_of_birth',
                  'next_of_kin_country', 'active', 'inactive_reason', 'living_status', 'patient_type',
                  'stage', 'created_at', 'last_updated_at', 'last_updated_overall_at', 'created_by',
                  'rdrf_registry', 'patientaddress_set', 'working_groups', 'consents',
                  'preferred_contact', 'insurance_data')

    def resolve_is_duplicate_patient(self, info):
        return self.duplicate_patient.is_duplicate

    def resolve_primary_carer(self, info):
        return self.primary_carers.first()

    def resolve_primary_carer_relationship(self, info):
        primary_carer = self.primary_carers.first()
        return PrimaryCarerRelationship.objects.filter(carer=primary_carer, patient=self).first().relationship
