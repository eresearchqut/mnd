import re

field_mappings = {
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
    ("myCommunication", "mndComms", "mndComChairOther"): "commMoreInfo",

    # My positioning
    ("mndPositioning", "mostComfyPos", "myMostComfy"): "comfy_pos",
    ("mndPositioning", "inBed", "mndLieFlat"): "lie_flat",
    ("mndPositioning", "inBed", "mndMove"): "move",
    ("mndPositioning", "inBed", "mndNeedHelp"): "checkbox_mappings",
    ("mndPositioning", "inBed", "mndNeedUse"): "checkbox_mappings",
    ("mndPositioning", "mostComfyPos", "mndComfyOther"): "mndPosOther",
    ("mndPositioning", "inBed", "mndNotes"): "mndPosED",
    ("mndPositioning", "mndSitting", "mndChairNeed"): "checkbox_mappings",
    ("mndPositioning", "mndSitting", "mndChairNotes"): "mndPosSD",
    ("mndPositioning", "mndSitting", "mndChairMove"): "move_chair",

    # My breathing
    ("myBreathing", "mndBreathing", "mndBreathHard"): "bre_trouble",
    ("myBreathing", "mndBreathing", "mndWhenBreathHard"): "checkbox_mappings",
    ("myBreathing", "mndBreathing", "mndNIVYN"): "niv",
    ("myBreathing", "mndBreathing", "mndBreathAssist"): "checkbox_mappings",
    ("myBreathing", "mndBreathing", "mndBAOther"): "mndBreathingOM",
    ("myBreathing", "mndBreathing", "mndNIV"): "checkbox_mappings",
    ("myBreathing", "mndBreathing", "mndNIVUse"): "checkbox_mappings",

    # My eating and drinking needs
    ("myEatDrink", "mndEating", "mndSwallowD"): "swal",
    ("myEatDrink", "mndEating", "mndByMouth"): "eat_bm",
    ("myEatDrink", "mndEating", "mndHelpEat"): "help_ed",
    ("myEatDrink", "mndEating", "mndACC"): "adapted_cc",
    ("myEatDrink", "mndEating", "mndFluids"): "fluid_lvl",
    ("myEatDrink", "mndEating", "mndFoodCon"): "food_lvl",
    ("myEatDrink", "mndEating", "mndPEG"): "peg",
    ("myEatDrink", "mndEating", "mndTube"): "checkbox_mappings",
    ("myEatDrink", "mndEating", "mndTubeDetails"): "ft_details",
    ("myEatDrink", "mndEating", "mndAvoidFoods"): "checkbox_mappings",
    ("myEatDrink", "mndEating", "mndGluten"): "gluten_details",
    ("myEatDrink", "mndEating", "mndDairy"): "dairy_details",
    ("myEatDrink", "mndEating", "mndPeanuts"): "peanuts_details",
    ("myEatDrink", "mndEating", "mndSoy"): "soy_details",
    ("myEatDrink", "mndEating", "mndEggs"): "eggs_details",
    ("myEatDrink", "mndEating", "mndShell"): "shellfish_details",
    ("myEatDrink", "mndEating", "mndRed"): "rm_details",
    ("myEatDrink", "mndEating", "mndWhite"): "wm_details",
    ("myEatDrink", "mndEating", "mndFish"): "fish_details",
    ("myEatDrink", "mndEating", "mndFoodPrefer"): "prefer_free-text",
    ("myEatDrink", "mndEating", "mndAvoidOther"): "avoid_other",
    # ("myEatDrink", "mndEating", "mndOther"): "",

    # My physical ability
    ("myPhysical", "physicalAbility", "mndWeakness"): "checkbox_mappings",
    ("myPhysical", "physicalAbility", "mndPhyUse"): "checkbox_mappings",
    ("myPhysical", "physicalAbility", "mndWalking"): "walk?",
    # ("myPhysical", "physicalAbility", "mndTransHelp"): "transfer", -> needs to be checkbox in the pdf
    ("myPhysical", "physicalAbility", "mndMoveAids"): "move-around_fill",
    ("myPhysical", "physicalAbility", "mndTaskAids"): "do-things_fill",
    ("myPhysical", "physicalAbility", "mndRestNeeded"): "rest_fill",

    # My personal care
    ("myPC", "personalCare", "mndPHygiene"): "hygiene",  # button has lower case "some" option instead of "Some"
    ("myPC", "personalCare", "mndShower"): "shower",
    ("myPC", "personalCare", "mndDress"): "dress",
    ("myPC", "personalCare", "mndToil"): "toilet",
    ("myPC", "personalCare", "mndCareNeeds"): "personal-care",

    # My mouth care and saliva
    ("myMCare", "mndMouth", "mndMHelp"): "mouth_care",
    ("myMCare", "mndMouth", "mndBrush"): "brush-teeth",
    ("myMCare", "mndMouth", "mndSwabs"): "swabs",
    # ("myMCare", "mndMouth", "mndXSaliva"): 'Sometimes',
    ("myMCare", "mndMouth", "mndManageSaliva"): "checkbox_mappings",
    ("myMCare", "mndMouth", "mndSalivaOther"): "sm_other",

    # My emotions
    ("myEmotions", "mndEmotionCare", "mndEmotionNotes"): "emotions_fill",

    # My medications and allergies
    ("myMedsNAll", "myAllergies", "mndAllergies"): "allergies_text",
    ("myMedsNAll", "myMedList", "mndDateStarted"): "start_date1",
    ("myMedsNAll", "myMedList", "mndMedName"): "med_name1",
    ("myMedsNAll", "myMedList", "mndMedDose"): "med_dose1",
    ("myMedsNAll", "myMedList", "mndMedPurpose"): "med_use1",
    # ("myMedsNAll", "myMedList", "mndMedFreq"): 'Every 12 Hours',
    # ("myMedsNAll", "myMedList", "mndMedOther"): '',
    # ("myMedsNAll", "myMedList", "mndMedTime"): '07:55 AM',
    # ("myMedsNAll", "myMedList", "mndMedTime2"): '07:55 PM',
    # ("myMedsNAll", "myMedList", "mndMedTime3"): '',
    # ("myMedsNAll", "myMedList", "mndMedTime4"): '',
    # ("myMedsNAll", "myMedList", "mndMedTime5"): '',
    # ("myMedsNAll", "myMedList", "mndMedTime6"): '',
    # ("myMedsNAll", "myMedList", "mndMedTime6Plus"): '',
    # ("myMedsNAll", "myMedList", "mndMedAdmin"): 'Via Nebuliser',

    # My appointments
    ('myAppointments', 'mndApptList', 'mndAName'): "Name of Team memberRow1",
    ('myAppointments', 'mndApptList', 'mndApptDate'): "Date of appointmentRow1",
    ('myAppointments', 'mndApptList', 'mndApptTime'): "TimeRow1",

    # My care team
    ("myCareTeam", "myCarerDetails", "mndCRole"): "mndCarerProfession1",
    ("myCareTeam", "myCarerDetails", "mndCName"): "NameRow1",
    # ("myCareTeam", "myCarerDetails", "mndCAddress"): "Address Team Member 1",
    ("myCareTeam", "myCarerDetails", "mndCPhone"): "TelephoneRow1",
    ("myCareTeam", "myCarerDetails", "mndCEmail"): "EmailRow1",
    # ("myCareTeam", "myCarerDetails", "mndPrimary"): ["PrimaryContact"],
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
