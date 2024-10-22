from ehrql.tables.tpp import patients, case, when, clinical_events

from pf_variables_library import check_pregnancy_status, count_past_events

# Create dictionary of pharmacy first codes
pharmacy_first_event_codes = {
    # # Community Pharmacy (CP) Blood Pressure (BP) Check Service (procedure)
    # "blood_pressure_service": ["1659111000000107"],
    # # Community Pharmacy (CP) Contraception Service (procedure)
    # "contraception_service": ["1659121000000101"],
    # Community Pharmacist (CP) Consultation Service for minor illness (procedure)
    "consultation_service": ["1577041000000109"],
    # Pharmacy First service (qualifier value)
    "pharmacy_first_service": ["983341000000102"],
    "combined_pf_service": ["1577041000000109", "983341000000102"],
}

def get_pf_consultation_ids():
    pharmacy_first_ids = clinical_events.where(
    clinical_events.snomedct_code.is_in(pharmacy_first_event_codes["combined_pf_service"])
    ).consultation_id
    return pharmacy_first_ids

def get_pf_clinical_events(pharmacy_first_ids):
    selected_events = clinical_events.where(clinical_events.consultation_id.is_in(pharmacy_first_ids))
    return selected_events

# Create denominator variables for each clinical condition
# These are based on NHS England rules using sex, age, pregnancy status and repeated diagnoses
# NOTE: The following exclusions have not been added:
# - urinary catheter for URT,
# - bullous impetigo,
# - chronic sinusitis and immunosuppressed individuals for acute sinusitis
def get_uncomplicated_uti_denominator(index_date, selected_events, pregnancy_codelist):
    urt_code = ["1090711000000102"]
    count_urt_6m = count_past_events(index_date, selected_events, urt_code, 6)
    count_urt_12m = count_past_events(index_date, selected_events, urt_code, 12)

    age = patients.age_on(index_date)
    pregnancy_status = check_pregnancy_status(
        index_date, selected_events, pregnancy_codelist
    )

    return (
        (age >= 16)
        & (age <= 64)
        & (patients.sex.is_in(["female"]) & pregnancy_status.is_null())
        | (count_urt_6m < 2)
        | (count_urt_12m < 3)
    )


def get_shingles_denominator(index_date, selected_events, pregnancy_codelist):
    age = patients.age_on(index_date)
    pregnancy_status = check_pregnancy_status(
        index_date, selected_events, pregnancy_codelist
    )

    return (age >= 18) & pregnancy_status.is_null()


def get_impetigo_denominator(index_date, selected_events, pregnancy_codelist):
    impetigo_code = ["48277006"]
    count_impetigo_12m = count_past_events(
        index_date, selected_events, impetigo_code, 12
    )

    age = patients.age_on(index_date)
    pregnancy_status = check_pregnancy_status(
        index_date, selected_events, pregnancy_codelist
    )

    return (
        (age >= 1)
        | (pregnancy_status.is_not_null() & (age >= 16))
        | (count_impetigo_12m < 2)
    )


def get_infected_insect_bites_denominator(
    index_date, selected_events, pregnancy_codelist
):
    age = patients.age_on(index_date)
    pregnancy_status = check_pregnancy_status(
        index_date, selected_events, pregnancy_codelist
    )

    return (age >= 1) | (pregnancy_status.is_not_null() & (age >= 16))


def get_acute_sore_throat_denominator(index_date, selected_events, pregnancy_codelist):
    age = patients.age_on(index_date)
    pregnancy_status = check_pregnancy_status(
        index_date, selected_events, pregnancy_codelist
    )

    return (age >= 5) | (pregnancy_status.is_not_null() & (age >= 16))


def get_acute_sinusitis_denominator(index_date, selected_events, pregnancy_codelist):
    age = patients.age_on(index_date)
    pregnancy_status = check_pregnancy_status(
        index_date, selected_events, pregnancy_codelist
    )

    return (age >= 12) | (pregnancy_status.is_not_null() & (age >= 16))


def get_acute_otitis_media_denominator(index_date, selected_events, pregnancy_codelist):
    acute_otitis_code = ["3110003"]
    count_acute_otitis_6m = count_past_events(
        index_date, selected_events, acute_otitis_code, 6
    )
    count_acute_otitis_12m = count_past_events(
        index_date, selected_events, acute_otitis_code, 12
    )

    age = patients.age_on(index_date)
    pregnancy_status = check_pregnancy_status(
        index_date, selected_events, pregnancy_codelist
    )

    return (
        (age >= 1) & (age <= 17)
        | (pregnancy_status.is_not_null() & (age >= 16))
        | (count_acute_otitis_6m < 3)
        | (count_acute_otitis_12m < 4)
    )


def get_latest_ethnicity(index_date, clinical_events, ethnicity_codelist, ethnicity_from_sus):
    latest_ethnicity_from_codes_category_num = (
        clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
        .where(clinical_events.date.is_on_or_before(index_date))
        .sort_by(clinical_events.date)
        .last_for_patient()
        .snomedct_code.to_category(ethnicity_codelist)
    )

    latest_ethnicity_from_codes = case(
        when(latest_ethnicity_from_codes_category_num == "1").then("White"),
        when(latest_ethnicity_from_codes_category_num == "2").then("Mixed"),
        when(latest_ethnicity_from_codes_category_num == "3").then(
            "Asian or Asian British"
        ),
        when(latest_ethnicity_from_codes_category_num == "4").then(
            "Black or Black British"
        ),
        when(latest_ethnicity_from_codes_category_num == "5").then(
            "Chinese or Other Ethnic Groups"
        ),
    )

    ethnicity_from_sus = case(
        when(ethnicity_from_sus.code.is_in(["A", "B", "C"])).then("White"),
        when(ethnicity_from_sus.code.is_in(["D", "E", "F", "G"])).then("Mixed"),
        when(ethnicity_from_sus.code.is_in(["H", "J", "K", "L"])).then(
            "Asian or Asian British"
        ),
        when(ethnicity_from_sus.code.is_in(["M", "N", "P"])).then("Black or Black British"),
        when(ethnicity_from_sus.code.is_in(["R", "S"])).then(
            "Chinese or Other Ethnic Groups"
        ),
    )

    ethnicity_combined = case(
        when(latest_ethnicity_from_codes.is_not_null()).then(latest_ethnicity_from_codes),
        when(latest_ethnicity_from_codes.is_null() & ethnicity_from_sus.is_not_null()).then(
            ethnicity_from_sus
        ),
        otherwise="Missing",
    )

    return(ethnicity_combined)
