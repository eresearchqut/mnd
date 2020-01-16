import pycountry

from ..settings import PDF_TEMPLATES_PATH
from ..models import PrimaryCarerRelationship


def _yes_no(input):
    return "Yes" if input else "No"


def _yes_no_not_available(input):
    if input is None:
        return "NA"
    return _yes_no(input)


def _generate_patient_fields(patient):
    return {
        'pFirstName': patient.given_names,
        'pLastName': patient.family_name,
        'pMaidenName': patient.maiden_name,
        'pDOB': patient.date_of_birth.strftime("%d/%m/%Y") if patient.date_of_birth else '',
        'pPhoneNo': patient.home_phone,
        'pMobile': patient.mobile_phone,
        'pEmail': patient.email,
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
        return input.capitalize() if input else ''

    def ndis_full_name(insurance):
        fn = insurance.ndis_coordinator_first_name
        ln = insurance.ndis_coordinator_last_name
        return ' '.join(n for n in (fn, ln) if n)

    if not insurance:
        return {}

    result = {
        'pPension': insurance.pension_number,
        'pMedicare': insurance.medicare_number,
        'pNDIS': _yes_no(patient.age >= 65),
        'pNDISNumber': insurance.ndis_number,
        'pNDISPM': ndis_plan_manager(insurance.ndis_plan_manager),
        'NDISName': ndis_full_name(insurance),
        'NDISPhone': insurance.ndis_coordinator_phone,
        'NDISEmail': insurance.ndis_coordinator_email,
        'pPrivateHealth': _yes_no(insurance.private_health_fund),
        'pDVACard': _yes_no(insurance.dva_card_number),
        'pMAC': _yes_no_not_available(insurance.referred_for_mac_care),
        'comHCP': _yes_no(insurance.eligible_for_home_care),
        'comHCPLevel': insurance.needed_mac_level,
        'recHCP': _yes_no(insurance.receiving_home_care),
        'recHCPLevel': insurance.home_care_level,
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
            'primary_carer': 'Carer'
        }
        return mapping.get(preferred_contact.contact_method, 'Off')

    if not preferred_contact:
        return {}
    return {
        'pPrefered': carer_contact_method(preferred_contact),
        'p3FName': preferred_contact.first_name,
        'p3LName': preferred_contact.last_name,
        'p3Phone': preferred_contact.phone,
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

    def primary_carer_language(code):
        lang = pycountry.languages.get(alpha_2=code)
        return lang.name if lang else ''

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

    if not primary_carer:
        return {}
    result = {
        'p2Relationship': primary_carer_relationship(primary_carer),
        'p2FName': primary_carer.first_name,
        'p2LName': primary_carer.last_name,
        'p2Email': primary_carer.email,
        'p2Phone': primary_carer.phone,
        'p2Lang': primary_carer_language(primary_carer.preferred_language),
        'same_address': primary_carer.same_address,
        'p2Interpreter': _yes_no(primary_carer.interpreter_required),
    }
    result.update(primary_carer_address(primary_carer, patient_address))
    return result


def generate_pdf_form_fields(registry, patient):
    data = _generate_patient_fields(patient)
    patient_address = patient.home_address
    data.update(_generate_patient_address_fields(patient_address))
    insurance = getattr(patient, 'insurance_data', None)
    data.update(_generate_patient_insurance_fields(patient, insurance))
    preferred_contact = getattr(patient, 'preferred_contact', None)
    data.update(_generate_preferred_contact_fields(preferred_contact))
    primary_carer = patient.primary_carers.first()
    data.update(_generate_primary_carer_fields(primary_carer, patient, patient_address))

    # TODO
    # dynamic_data = patient.get_dynamic_data(registry)

    return {k: '' if v is None else v for k, v in data.items()}


def get_pdf_template():
    return f"{PDF_TEMPLATES_PATH}/About me and MND_Interactive_v5a.pdf"
