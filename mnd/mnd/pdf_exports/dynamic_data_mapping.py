import re

# key is (section_code, cde_code), value is pdf form element
_single_section_field_mappings = {
    # My legal docs
    ("legalQuestions", "mndACD"): "acd",
    ("legalQuestions", "mndLDocs"): "checkbox_mappings",
    ("legalQuestions", "mndDocLocation"): "pDocuments",

    # My MND
    ("mndType", "mndTypeSelect"): "mndType",
    ("mndType", "mndDiagDate"): "mndDiagDate",
    ("mndType", "mndALSFRSSum"): "alsfrsScore",
    ("mndType", "mndALSTestDate"): "mndTestDate_af_date",

    # My recent symptoms
    ("symptomTypes", "mndSymptomDate"): "mndSymptomsDate_af_date",
    ("symptomTypes", "mndFatigue"): "fatigue",
    ("symptomTypes", "mndPain"): "pain",
    ("symptomTypes", "mndMuscle"): "cramps",
    ("symptomTypes", "mndSaliva"): "saliva",
    ("symptomTypes", "mndConstipation"): "constipation",
    ("symptomTypes", "mndDisSleep"): "dSleep",
    ("symptomTypes", "mndBreath"): "sBreath",
    ("symptomTypes", "mndSpasticity"): "stiffSpas",
    ("symptomTypes", "mndChoking"): "choking",
    ("symptomTypes", "mndDepression"): "depression",
    ("symptomTypes", "mndEmotion"): "emotion",

    # My Life History
    ("mndHistoryNotes", "mndLHLife"): "life_history",
    ("mndHistoryNotes", "mndLHWork"): "work_history",
    ("mndHistoryNotes", "mndLHFriends"): "family_friends",
    ("mndHistoryNotes", "mndLHDaily"): "daily_routines",
    ("mndHistoryNotes", "mndLHHobbies"): "hobbies_text",
    ("mndHistoryNotes", "mndLHChat"): "enjoyable_topics",
    ("mndHistoryNotes", "mndLHMusic"): "radio_music",
    ("mndHistoryNotes", "mndLHTV"): "favourite_tv",
    ("mndHistoryNotes", "mndLHFilms"): "favourite_films",
    ("mndHistoryNotes", "mndLHBooks"): "favourite_books",
    ("mndHistoryNotes", "mndLHSocialMedia"): "favourite_blogs",
    ("mndHistoryNotes", "mndLHAnnoyances"): "dislikes_text",
    ("mndHistoryNotes", "mndLHWorries"): "worries_text",
    ("mndHistoryNotes", "mndLHRemedies"): "anxious_text",

    # My Past medical history
    ("mndMHDiagnosis", "mndConditions"): "checkbox_mappings",
    ("mndMHDiagnosis", "mndCondOther"): "mh_other",

    # My Communication
    ("mndComms", "mndComDifficulty"): "commLevel",
    ("mndComms", "mndComTechs"): "checkbox_mappings",
    ("mndComms", "mndComChairOther"): "commMoreInfo",

    # My positioning
    ("mostComfyPos", "myMostComfy"): "comfy_pos",
    ("mostComfyPos", "mndComfyOther"): "mndPosOther",
    ("inBed", "mndLieFlat"): "lie_flat",
    ("inBed", "mndMove"): "move",
    ("inBed", "mndNeedHelp"): "checkbox_mappings",
    ("inBed", "mndNeedUse"): "checkbox_mappings",
    ("inBed", "mndNotes"): "mndPosED",
    ("mndSitting", "mndChairNeed"): "checkbox_mappings",
    ("mndSitting", "mndChairNotes"): "mndPosSD",
    ("mndSitting", "mndChairMove"): "move_chair",

    # My breathing
    ("mndBreathing", "mndBreathHard"): "bre_trouble",
    ("mndBreathing", "mndWhenBreathHard"): "checkbox_mappings",
    ("mndBreathing", "mndNIVYN"): "niv",
    ("mndBreathing", "mndBreathAssist"): "checkbox_mappings",
    ("mndBreathing", "mndBAOther"): "mndBreathingOM",
    ("mndBreathing", "mndNIV"): "checkbox_mappings",
    ("mndBreathing", "mndNIVUse"): "checkbox_mappings",

    # My eating and drinking needs
    ("mndEating", "mndSwallowD"): "swal",
    ("mndEating", "mndByMouth"): "eat_bm",
    ("mndEating", "mndHelpEat"): "help_ed",
    ("mndEating", "mndACC"): "adapted_cc",
    ("mndEating", "mndFluids"): "fluid_lvl",
    ("mndEating", "mndFoodCon"): "food_lvl",
    ("mndEating", "mndPEG"): "peg",
    ("mndEating", "mndTube"): "checkbox_mappings",
    ("mndEating", "mndTubeDetails"): "ft_details",
    ("mndEating", "mndAvoidFoods"): "checkbox_mappings",
    ("mndEating", "mndGluten"): "gluten_details",
    ("mndEating", "mndDairy"): "dairy_details",
    ("mndEating", "mndPeanuts"): "peanuts_details",
    ("mndEating", "mndSoy"): "soy_details",
    ("mndEating", "mndEggs"): "eggs_details",
    ("mndEating", "mndShell"): "shellfish_details",
    ("mndEating", "mndRed"): "rm_details",
    ("mndEating", "mndWhite"): "wm_details",
    ("mndEating", "mndFish"): "fish_details",
    ("mndEating", "mndFoodPrefer"): "prefer_free-text",
    ("mndEating", "mndAvoidOther"): "avoid_other",
    # ("mndEating", "mndOther"): "",

    # My physical ability
    ("physicalAbility", "mndWeakness"): "checkbox_mappings",
    ("physicalAbility", "mndPhyUse"): "checkbox_mappings",
    ("physicalAbility", "mndWalking"): "walk?",
    # ("physicalAbility", "mndTransHelp"): "transfer", -> needs to be checkbox in the pdf
    ("physicalAbility", "mndMoveAids"): "move-around_fill",
    ("physicalAbility", "mndTaskAids"): "do-things_fill",
    ("physicalAbility", "mndRestNeeded"): "rest_fill",

    # My personal care
    ("personalCare", "mndPHygiene"): "hygiene",  # button has lower case "some" option instead of "Some"
    ("personalCare", "mndShower"): "shower",
    ("personalCare", "mndDress"): "dress",
    ("personalCare", "mndToil"): "toilet",
    ("personalCare", "mndCareNeeds"): "personal-care",

    # My mouth care and saliva
    ("mndMouth", "mndMHelp"): "mouth_care",
    ("mndMouth", "mndBrush"): "brush-teeth",
    ("mndMouth", "mndSwabs"): "swabs",
    ("mndMouth", "mndXSaliva"): "saliva",
    ("mndMouth", "mndManageSaliva"): "checkbox_mappings",
    ("mndMouth", "mndSalivaOther"): "sm_other",

    # My emotions
    ("mndEmotionCare", "mndEmotionNotes"): "emotions_fill",

    # My medications and allergies
    ("myAllergies", "mndAllergies"): "allergies_text",
}

# key is (section_code, cde_code), value is pdf form element base (and index is appended..usually from 1 to 9)
_multi_section_field_mappings = {
    # My medications and allergies
    ("myMedList", "mndDateStarted"): "start_date",
    ("myMedList", "mndMedName"): "med_name",
    ("myMedList", "mndMedDose"): "med_dose",
    ("myMedList", "mndMedPurpose"): "med_use",
    ("myMedList", "mndMedAdmin"): "med_taken",
    ("myMedList", "mndMedTime"): "med_times",

    # My appointments
    ("mndApptList", "mndAName"): "Name of Team memberRow",
    ("mndApptList", "mndApptDate"): "Date of appointmentRow",
    ("mndApptList", "mndApptTime"): "TimeRow",

    # My care team
    ("myCarerDetails", "mndCRole"): "mndCarerProfession",
    ("myCarerDetails", "mndCName"): "NameRow",
    ("myCarerDetails", "mndCPhone"): "TelephoneRow",
    ("myCarerDetails", "mndCEmail"): "EmailRow",
}

_care_team_section = "myCarerDetails"
_care_team_primary_carer_cde = "mndPrimary"


def _interval_mapping(input_val):
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


def _comfy_pos_mapping(input_val):
    mappings = {
        "In bed": "bed",
        "In my wheelchair": "wheelchair",
        "In a comfortable chair (e.g. Recliner)": "Chair"
    }
    return mappings.get(input_val, "")


def _mnd_type_mapping(input_val):
    mappings = {
        "ALS - Amyotrophic Lateral Sclerosis": "ALS",
        "PBP - Primary Bulbar Palsy": "PBP",
        "PLS - Primary Lateral Sclerosis": "PLS",
        "PMA - Primary Muscular Atrophy": "PMA",
        "Unsure": "Unsure"
    }
    return mappings.get(input_val, "")


def _eat_drink_by_mouth_mapping(input_val):
    mappings = {
        "Yes": "Yes",
        "Some types": "Some",
        "No": "No"
    }
    return mappings.get(input_val, "")


def _help_eat_mapppings(input_val):
    mappings = {
        "I need to be fed": "Need",
        "Some help": "some",
        "No": "No"
    }
    return mappings.get(input_val, "")


def _level_mapping(input_val):
    result = re.match(r"^Level\s(\d+)(.)*", input_val)
    if result and result.groups():
        return result.groups()[0]


def _avoid_details_mapping(input_val):
    mappings = {
        "Allergy": "Allergy",
        "Intolerance": "Intolerance",
        "Lifestyle Choice": "Lifestyle_Choice"
    }
    return mappings.get(input_val, "")


def _walk_values_mapping(input_val):
    mappings = {
        "Yes": "Yes",
        "No": "No",
        "With Support or Aids": "need_aid"
    }
    return mappings.get(input_val, "")


def _brush_teeth_mapping(input_val):
    mappings = {
        "Once a day": "Once",
        "Twice daily": "Twice",
        "Three times a day": "3-times"
    }
    return mappings.get(input_val, "")


_values_mapping_cdes = {
    "mndFatigue": _interval_mapping,
    "mndPain": _interval_mapping,
    "mndMuscle": _interval_mapping,
    "mndSaliva": _interval_mapping,
    "mndConstipation": _interval_mapping,
    "mndDisSleep": _interval_mapping,
    "mndBreath": _interval_mapping,
    "mndSpasticity": _interval_mapping,
    "mndChoking": _interval_mapping,
    "mndDepression": _interval_mapping,
    "mndEmotion": _interval_mapping,
    "mndComDifficulty": _communication_value_mapping,
    "myMostComfy": _comfy_pos_mapping,
    "mndTypeSelect": _mnd_type_mapping,
    "mndByMouth": _eat_drink_by_mouth_mapping,
    "mndHelpEat": _help_eat_mapppings,
    "mndFluids": _level_mapping,
    "mndFoodCon": _level_mapping,
    "mndGluten": _avoid_details_mapping,
    "mndDairy": _avoid_details_mapping,
    "mndPeanuts": _avoid_details_mapping,
    "mndSoy": _avoid_details_mapping,
    "mndEggs": _avoid_details_mapping,
    "mndShell": _avoid_details_mapping,
    "mndRed": _avoid_details_mapping,
    "mndWhite": _avoid_details_mapping,
    "mndFish": _avoid_details_mapping,
    "mndWalking": _walk_values_mapping,
    "mndBrush": _brush_teeth_mapping,
}


_checkbox_mapping_cdes = {
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
    },
    "mndNeedHelp": {
        "Sit Up": "sit",
        "Turn Over": "turn_over",
        "Change Position": "change_pos"
    },
    "mndNeedUse": {
        "An adjustable bed": "adj_bed",
        "Extra pillows": "ex_pillows",
        "Pressure relieving mattress": "prm",
        "Bed cradle": "bed_cradle",
        "Neck support when sitting up": "neck_support",
    },
    "mndChairNeed": {
        "A lift or electric recliner": "lift_e-rec",
        "Pressure relief": "pressure_relief",
        "Head or neck support": "head_neck_support",
        "An electric wheelchair": "e-wheelchair",
    },
    "mndWhenBreathHard": {
        "At rest": "rest",
        "Moving around": "moving",
        "Moving a lot": "moving_lots"
    },
    "mndBreathAssist": {
        "Suctioning": "suct",
        "Assisted cough techniques": "act",
        "A fan": "fan",
        "Positioning": "bre_pos"
    },
    "mndNIV": {
        "Whenever I sleep": "niv_sleep",
        "When needed": "niv_needed",
        "Most of the time": "niv_mostly",
    },
    "mndNIVUse": {
        "Independent": "niv_ind",
        "Need some assistance": "niv_some_help",
        "Need full assistance": "niv_full_assist"
    },
    "mndTube": {
        # Cannot find option in PDF for all options
        "For hydration": "hydration",
        "To top up my meals": "meals",
        "For all food and drink": "all_fd",
        "I need help with my tube feeds": "ft_help",
    },
    "mndAvoidFoods": {
        "Gluten": "gluten",
        "Dairy": "dairy",
        "Peanuts": "peanuts",
        "Soy": "soy",
        "Eggs": "eggs",
        "Shellfish": "shellfish",
        "Read Meat": "red_meat",
        "White Meat": "white_meat",
        "Fish": "fish",
    },
    "mndWeakness": {
        "Upper Limbs": "u_limbs",
        "Lower Limbs": "l_limbs",
        "Head/Neck": "head_neck",
        "Trunk": "trunk",
    },
    "mndPhyUse": {
        "Arm/Wrist Splints": "aw_splints",
        "Leg/Foot Splints": "lf_splints",
        "Head/Neck Support": "hn_support",
    },
    "mndManageSaliva": {
        "Medication": "sm_meds",
        "Suction": "sm_suction",
        "Clothing Protection": "sm_clothing-p",
        "Swallowing": "sm_swallowing",
        "Clearance Techniques": "sm_clearance",
        "Wiping Mouth": "smWiping",
    }
}


def _set_data_fields(data, field, cde_code, value):
    if cde_code in _values_mapping_cdes:
        mapping_func = _values_mapping_cdes[cde_code]
        data[field] = mapping_func(value)
    elif cde_code in _checkbox_mapping_cdes:
        mappings = _checkbox_mapping_cdes[cde_code]
        if isinstance(value, list):
            checkbox_updates = {mappings[v]: "Yes" for v in value if v in mappings}
        else:
            checkbox_updates = {mappings[v]: "Yes" for v in [value] if v in mappings}
        data.update(checkbox_updates)
    else:
        data[field] = value


def _get_primary_carer_section_index(form_values):
    for section_index in range(1, 10):
        key = (_care_team_section, _care_team_primary_carer_cde, section_index)
        if key in form_values:
            value = form_values[key]
            if value and value[0] == "PrimaryContact":
                return section_index
    return 1


def generate_pdf_field_mappings(form_values):
    data = {}
    for (section_code, cde_code), field in _single_section_field_mappings.items():
        single_section_key = (section_code, cde_code, 0)
        value = form_values[single_section_key]
        _set_data_fields(data, field, cde_code, value)

    primary_carer_index = _get_primary_carer_section_index(form_values)
    section_indexes = range(1, 10)
    carer_indexes = list(range(1, 10))
    if primary_carer_index != 1:
        carer_indexes.remove(primary_carer_index)
        carer_indexes.insert(0, primary_carer_index)

    for (section_code, cde_code), field in _multi_section_field_mappings.items():
        indexes = carer_indexes if section_code == _care_team_section else section_indexes
        for idx, i in enumerate(indexes):
            indexed_field = f"{field}{idx + 1}"
            if field == "med_times":
                # special handling for medicine administration times
                suffixes = ["", "2", "3", "4", "5", "6", "6Plus"]
                keys = [(section_code, cde_code + suffix, i) for suffix in suffixes]
                if any(k in form_values for k in keys):
                    values = [form_values[k] for k in keys if k in form_values]
                    value = ", ".join([v for v in values if v])
                    _set_data_fields(data, indexed_field, cde_code, value)
            else:
                section_key = (section_code, cde_code, i)
                if section_key in form_values:
                    value = form_values[section_key]
                    _set_data_fields(data, indexed_field, cde_code, value)

    return data
