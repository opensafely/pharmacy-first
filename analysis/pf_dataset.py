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
