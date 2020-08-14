import logging

from rdrf.models.definition.models import CommonDataElement

logger = logging.getLogger(__name__)


def _get_form_values(dyn_data):
    form_values = {}
    for form_dict in dyn_data["forms"]:
        form_name = form_dict["name"]
        for section_dict in form_dict["sections"]:
            section_code = section_dict["code"]
            if not section_dict["allow_multiple"]:
                for cde_dict in section_dict["cdes"]:
                    cde_code = cde_dict["code"]
                    form_values[(form_name, section_code, cde_code)] = cde_dict["value"]
            else:
                items = section_dict["cdes"]
                for cde_dict in items[0]:  # first section from multiple forms
                    form_values[(form_name, section_code, cde_code)] = cde_dict["value"]
    return form_values


_field_mappings = {
    # My legal docs
    ("myLegalDocs", "legalQuestions", "mndACD"): "acd",
    ("myLegalDocs", "legalQuestions", "mndLDocs"): "checkbox_mappings",
    ("myLegalDocs", "legalQuestions", "mndDocLocation"): "pDocuments",

    # My MND
    ("myMND", "mndType", "mndTypeSelect"): "mndType",
    ("myMND", "mndType", "mndDiagDate"): "mndDiagDate",
    ("myMND", "mndType", "mndALSFRSSum"): "alsfrsScore",
    ("myMND", "mndType", "mndALSTestDate"): "mndTestDate_af_date",

    # My recent symptoms
    ("mySymptoms", "symptomTypes", "mndSymptomDate"): "mndSymptomsDate_af_date",
    ("mySymptoms", "symptomTypes", "mndFatigue"): "fatigue",
    ("mySymptoms", "symptomTypes", "mndPain"): "pain",
    ("mySymptoms", "symptomTypes", "mndMuscle"): "cramps",
    ("mySymptoms", "symptomTypes", "mndSaliva"): "saliva",
    ("mySymptoms", "symptomTypes", "mndConstipation"): "constipation",
    ("mySymptoms", "symptomTypes", "mndDisSleep"): "dSleep",
    ("mySymptoms", "symptomTypes", "mndBreath"): "sBreath",
    ("mySymptoms", "symptomTypes", "mndSpasticity"): "stiffSpas",
    ("mySymptoms", "symptomTypes", "mndChoking"): "choking",
    ("mySymptoms", "symptomTypes", "mndDepression"): "depression",
    ("mySymptoms", "symptomTypes", "mndEmotion"): "emotion",

    # My Life History
    ("myPastLH", "mndHistoryNotes", "mndLHLife"): "life_history",
    ("myPastLH", "mndHistoryNotes", "mndLHWork"): "work_history",
    ("myPastLH", "mndHistoryNotes", "mndLHFriends"): "family_friends",
    ("myPastLH", "mndHistoryNotes", "mndLHDaily"): "daily_routines",
    ("myPastLH", "mndHistoryNotes", "mndLHHobbies"): "hobbies_text",
    ("myPastLH", "mndHistoryNotes", "mndLHChat"): "enjoyable_topics",
    ("myPastLH", "mndHistoryNotes", "mndLHMusic"): "radio_music",
    ("myPastLH", "mndHistoryNotes", "mndLHTV"): "favourite_tv",
    ("myPastLH", "mndHistoryNotes", "mndLHFilms"): "favourite_films",
    ("myPastLH", "mndHistoryNotes", "mndLHBooks"): "favourite_books",
    ("myPastLH", "mndHistoryNotes", "mndLHSocialMedia"): "favourite_blogs",
    ("myPastLH", "mndHistoryNotes", "mndLHAnnoyances"): "dislikes_text",
    ("myPastLH", "mndHistoryNotes", "mndLHWorries"): "worries_text",
    ("myPastLH", "mndHistoryNotes", "mndLHRemedies"): "anxious_text",

    # My Past medical history
    ("myMedHistory", "mndMHDiagnosis", "mndConditions"): "checkbox_mappings",
    ("myMedHistory", "mndMHDiagnosis", "mndCondOther"): "mh_other",

    # My Communication
    ("myCommunication", "mndComms", "mndComDifficulty"): "commLevel",
    ("myCommunication", "mndComms", "mndComTechs"): "checkbox_mappings",
    ("myCommunication", "mndComms", "mndComChairOther"): 'commMoreInfo'
}


def _value_mapping(input_val):
    if input_val == 0:
        return "none"
    if input_val < 5:
        return "mild"
    if input_val < 9:
        return "moderate"
    return "severe"


def _communication_value_mapping(input_val):
    mappings = {
        "no difficulty communicating": "No difficulty",
        "some difficulty communicating": "Some Difficulty",
        "great difficulty communicating": "Great difficulty"
    }
    return mappings.get(input_val, "")


values_mapping_cdes = {
    "mndFatigue": _value_mapping,
    "mndPain": _value_mapping,
    "mndMuscle": _value_mapping,
    "mndSaliva": _value_mapping,
    "mndConstipation": _value_mapping,
    "mndDisSleep": _value_mapping,
    "mndBreath": _value_mapping,
    "mndSpasticity": _value_mapping,
    "mndChoking": _value_mapping,
    "mndDepression": _value_mapping,
    "mndEmotion": _value_mapping,
    "mndComDifficulty": _communication_value_mapping
}


checkbox_mapping_cdes = {
    "mndConditions": {
        "Asthma": "mh_asthma",
        "Cancer": "mh_cancer",
        "Depression": "mh_depression",
        "Diabetes": "mh_diabetes",
        "Heart Disease": "mh_heart-disease",
        "Anxiety": "mh_anxiety",
        "High Blood Pressure": "mh_hbp",
    },
    "mndComTechs": {
        "paperPen": "commPen",
        "talkToText": "commTextApp",
        "commsBoard": "commBoard",
        "voiceAmplifier": "commVA",
        "eyeGaze": "commEyeGaze",
        "compWithSwitch": "commSwitch",
    },
    "mndLDocs": {
        "Enduring Power of Guardianship": "epg",
        "A Medical Power of Attorney": "mpa",
        "An Anticipatory Direction": "ad",
        "DNR Form": "dnr",
        "Organ and/or Tissue Donation": "otd",
    }
}


def generate_dynamic_data_fields(registry, patient):
    data = {}
    form_values = {}
    for context_model in patient.context_models:
        dyn_data = patient.get_dynamic_data(registry, context_id=context_model.id)
        if not dyn_data:
            continue
        form_values.update(_get_form_values(dyn_data))
    cde_codes = [code for (__, __, code) in form_values.keys()]
    with_pv_groups = CommonDataElement.objects.filter(code__in=cde_codes, pv_group__isnull=False)
    cde_values_mapping = {
        cde.code: cde.pv_group.cde_values_dict for cde in with_pv_groups
    }
    updated_form_values = {}
    for key, value in form_values.items():
        form, section, code = key
        if code in cde_values_mapping and value:
            if not isinstance(value, list):
                updated_form_values[(form, section, code)] = cde_values_mapping[code].get(value, value)
    form_values.update(updated_form_values)

    logger.info(f"form values= {form_values}")

    for key, field in _field_mappings.items():
        __, __, cde_code = key
        if cde_code in values_mapping_cdes:
            mapping_func = values_mapping_cdes[cde_code]
            data[field] = mapping_func(form_values[key])
        elif cde_code in checkbox_mapping_cdes:
            values = form_values[key]
            mappings = checkbox_mapping_cdes[cde_code]
            for v in values:
                if v in mappings:
                    data[mappings[v]] = "Yes"
        else:
            data[field] = form_values[key]

    return data
