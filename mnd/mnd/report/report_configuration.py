from report.report_configuration import get_configuration


def get_mnd_configuration():
    mnd_report_configuration = get_configuration()

    # Extend Reportable Demographic fields
    mnd_report_configuration['demographic_model']['patient']['fields'].update({
        'isDuplicatePatient': 'Is potential duplicate patient',
        'preferredContact { contactMethod }': 'Preferred contact method',
        'primaryCarerRelationship': 'Principal Carer Relationship',
    })

    # Add extra reportable models for MND
    mnd_report_configuration['demographic_model'].update({
        'primaryCarer': {
            'label': 'Principal Carer',
            'multi_field': False,
            'fields': {
                'firstName': 'First Name',
                'lastName': 'Last Name',
                'mobilePhone': 'Mobile phone',
                'homePhone': 'Home phone',
                'email': 'Email',
                'interpreterRequired': 'Interpreter required',
                'sameAddress': 'Same address?',
                'suburb': 'Suburb',
                'address': 'Address',
                'postcode': 'Postcode',
                'isEmergencyContact': 'Is emergency contact',
                'emContactFirstName': 'Emergency contact first name',
                'emContactLastName': 'Emergency contact last name',
                'emContactPhone': 'Emergency contact phone',
            }
        },
        'insuranceData': {
            'label': 'Medicare, Health insurance and support details',
            'multi_field': False,
            'fields': {
                'mainHospital': 'Main hospital',
                'mainHospitalMrn': 'Main hospital MRN',
                'secondaryHospital': 'Secondary hospital',
                'secondaryHospitalMrn': 'Secondary hospital MRN',
                'medicareNumber': 'Medicare number',
                'pensionNumber': 'Pension number',
                'hasPrivateHealthFund': 'Has private health fund',
                'privateHealthFund': 'Private health fund',
                'privateHealthFundNumber': 'Private health fund number',
                'isNdisParticipant': 'Is NDIS Participant?',
                'ndisNumber': 'NDIS number',
                'isNdisEligible': 'Is NDIS Eligible',
                'ndisPlanManager': 'NDIS plan manager',
                'ndisCoordinatorFirstName': 'NDIS coordinator first name',
                'ndisCoordinatorLastName': 'NDIS coordinator last name',
                'ndisCoordinatorPhone': 'NDIS coordinator phone',
                'ndisCoordinatorEmail': 'NDIS coordinator email',
                'hasDvaCard': 'Has DVA card?',
                'dvaCardNumber': 'DVA card number',
                'dvaCardType': 'DVA card type',
                'referredForMacCare': 'Referral for My Aged Care',
                'neededMacLevel': 'Needed My Aged Care level',
                'eligibleForHomeCare': 'Eligible for home care',
                'receivingHomeCare': 'Receiving home care',
                'homeCareLevel': 'Home care level',
            }
        }
    })

    return mnd_report_configuration
