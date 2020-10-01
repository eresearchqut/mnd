import pycountry

from ..settings import PDF_TEMPLATES_PATH
from ..models import PrimaryCarerRelationship, PrimaryCarer

from .dynamic_data_fields import generate_dynamic_data_fields


def _yes_no(input):
    return "Yes" if input else "No"


def _yes_no_off(input):
    if input is None:
        return "Off"
    return "Yes" if input else "No"


def _yes_no_not_available(input):
    if input is None:
        return "NA"
    return _yes_no(input)


def _gender_mapping(gender):
    mappings = {
        "1": "Male",
        "2": "Female",
        "3": "Other"
    }
    return mappings.get(gender, "Off")


def _language_mapping(code):
    lang = pycountry.languages.get(alpha_2=code)
    return lang.name if lang else ''


def _generate_patient_fields(patient):
    return {
        'pFirstName': patient.given_names,
        'pLastName': patient.family_name,
        'pMaidenName': patient.maiden_name,
        'pDOB': patient.date_of_birth.strftime("%d/%m/%Y") if patient.date_of_birth else '',
        'pPhoneNo': patient.home_phone,
        'pMobile': patient.mobile_phone,
        'pEmail': patient.email,
        'pGender': _gender_mapping(patient.sex),
    }


def _generate_patient_address_fields(patient_address):
    if not patient_address:
        return {}
    state_value_mapping = {
        'AU-SA': 'SA',
        'AU-ACT': 'ACT',
        'AU-NT': 'NT',
        'AU-TAS': 'TAS',
        'AU-QLD': 'QLD',
        'AU-WA': 'WA',
        'AU-VIC': 'VIC'
    }
    return {
        'pSuburb': patient_address.suburb,
        'pAddress': patient_address.address,
        'pPostcode': patient_address.postcode,
        'pState': state_value_mapping.get(patient_address.state, 'QLD') if patient_address.state else '',
    }


def _generate_patient_insurance_fields(patient, insurance):

    def ndis_plan_manager(input):
        mappings = {
            'self': 'Self',
            'agency': 'Agency',
            '': 'Off',
            'other': 'Plan Managed'
        }
        return mappings.get(input, 'Off')

    if not insurance:
        return {}

    result = {
        'pPension': insurance.pension_number,
        'pMedicare': insurance.medicare_number,
        'pNDIS': _yes_no(insurance.is_ndis_eligible),
        'pNDISNumber': insurance.ndis_number,
        'pNDISPM': 'Self' if insurance.is_ndis_participant else 'Off',
        'pNDISmgmt': ndis_plan_manager(insurance.ndis_plan_manager),
        'NDISFirstName': insurance.ndis_coordinator_first_name,
        'NDISPhone': insurance.ndis_coordinator_phone,
        'NDISEmail': insurance.ndis_coordinator_email,
        'pPrivateHealth': _yes_no(insurance.private_health_fund),
        'pDVACard': _yes_no(insurance.dva_card_number),
        'pMAC': _yes_no_not_available(insurance.referred_for_mac_care),
        'comHCP': _yes_no(insurance.eligible_for_home_care),
        'comHCPLevel': insurance.needed_mac_level,
        'recHCP': _yes_no(insurance.receiving_home_care),
        'recHCPLevel': insurance.home_care_level,
        'pMainHospital': insurance.main_hospital,
        'pMainHospitalMRN': insurance.main_hospital_mrn,
        'pSecondaryHospital': insurance.secondary_hospital,
        'pSecondaryHospitalMRN': insurance.secondary_hospital_mrn,
    }
    if insurance.private_health_fund:
        result.update({
            'pPHList': insurance.private_health_fund,
            'pPHNumber': insurance.private_health_fund_number,
        })
    if insurance.dva_card_number:
        result.update({
            'pDVAType': insurance.dva_card_type,
            'pDVANumber': insurance.dva_card_number
        })
    return result


def _generate_preferred_contact_fields(preferred_contact):

    def carer_contact_method(preferred_contact):
        mapping = {
            'phone': 'Phone',
            'sms': 'SMS',
            'email': 'Email',
            'primary_carer': 'Carer',
        }
        return mapping.get(preferred_contact.contact_method, 'Off')

    if not preferred_contact:
        return {}
    return {
        'pPrefered': carer_contact_method(preferred_contact),
    }


def _generate_language_info_fields(language_info):
    if not language_info:
        return {}

    return {
        'pLang': _language_mapping(language_info.preferred_language),
        'pInterpreter': _yes_no_off(language_info.interpreter_required),
    }


def _generate_primary_carer_fields(primary_carer, patient, patient_address):

    def primary_carer_relationship(primary_carer):
        mapping = {
            'spouse': 'Spouse/Partner',
            'child': 'Child',
            'sibling': 'Sibling',
            'friend': 'Friend',
            'other': 'Other'
        }
        relation = (
            PrimaryCarerRelationship
            .objects
            .filter(carer=primary_carer, patient=patient)
            .first()
        )
        if relation:
            return mapping.get(relation.relationship, 'Off')
        return 'Off'

    def primary_carer_address(primary_carer, patient_address):
        patient_adr = patient_address.address if patient_address else None
        patient_suburb = patient_address.suburb if patient_address else None
        patient_postcode = patient_address.postcode if patient_address else None
        address = patient_adr if primary_carer.same_address else primary_carer.address
        suburb = patient_suburb if primary_carer.same_address else primary_carer.suburb
        postcode = patient_postcode if primary_carer.same_address else primary_carer.postcode
        return {
            'p2Address': address,
            'p2Suburb': suburb,
            'p2Postcode': postcode
        }

    def emergency_contact_details(primary_carer):
        res = {}
        if primary_carer.is_emergency_contact:
            if primary_carer.first_name:
                res['p3FName'] = primary_carer.first_name
            if primary_carer.last_name:
                res['p3LName'] = primary_carer.last_name
            if primary_carer.phone:
                res['p3Phone'] = primary_carer.phone
        else:
            if primary_carer.em_contact_first_name:
                res['p3FName'] = primary_carer.em_contact_first_name
            if primary_carer.em_contact_last_name:
                res['p3LName'] = primary_carer.em_contact_last_name
            if primary_carer.em_contact_phone:
                res['p3Phone'] = primary_carer.em_contact_phone
        return res

    if not primary_carer:
        return {}

    result = {
        'p2Relationship': primary_carer_relationship(primary_carer),
        'p2FName': primary_carer.first_name,
        'p2LName': primary_carer.last_name,
        'p2Email': primary_carer.email,
        'p2HomePhone': primary_carer.home_phone,
        'p2MobilePhone': primary_carer.mobile_phone,
        'p2Lang': _language_mapping(primary_carer.preferred_language),
        'same_address': primary_carer.same_address,
        'p2Interpreter': _yes_no_off(primary_carer.interpreter_required),
    }
    result.update(primary_carer_address(primary_carer, patient_address))
    result.update(emergency_contact_details(primary_carer))
    return result


def generate_pdf_form_fields(registry, patient):
    data = _generate_patient_fields(patient)
    patient_address = patient.home_address
    data.update(_generate_patient_address_fields(patient_address))
    insurance = getattr(patient, 'insurance_data', None)
    data.update(_generate_patient_insurance_fields(patient, insurance))
    preferred_contact = getattr(patient, 'preferred_contact', None)
    data.update(_generate_preferred_contact_fields(preferred_contact))
    language_info = getattr(patient, 'language_info', None)
    data.update(_generate_language_info_fields(language_info))
    primary_carer = PrimaryCarer.get_primary_carer(patient)
    data.update(
        _generate_primary_carer_fields(primary_carer, patient, patient_address)
    )
    data.update(
        generate_dynamic_data_fields(registry, patient)
    )

    return {k: '' if v is None else v for k, v in data.items()}


def get_pdf_template():
    return f"{PDF_TEMPLATES_PATH}/MiNDAUS About Me and MND Form v10.pdf"
