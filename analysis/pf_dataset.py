from ehrql.tables.tpp import case, when
from pf_variables_library import check_pregnancy_status, count_past_events

# This file contains functions for the denominators of the patient population for each clinical condition.
# It will be used to calculate rates, and is separate from pf_variables_library


def has_event(events, codelist):
    return events.where(events.snomedct_code.is_in(codelist)).exists_for_patient()


# Create denominator variables for each clinical condition
# These are based on NHS England rules using sex, age, pregnancy status and repeated diagnoses
# NOTE: The following exclusions have not been added:
# - urinary catheter for URT,
# - bullous impetigo,
# - chronic sinusitis and immunosuppressed individuals for acute sinusitis
def get_numerator(
    index_date,
    patients,
    pregnancy_codelist,
    selected_events,
    condition_code,
    clinical_pathway,
):
    age = patients.age_on(index_date)
    pregnancy_status = check_pregnancy_status(
        index_date, selected_events, pregnancy_codelist
    )

    inclusion_criteria = False
    exclusion_criteria = False

    if clinical_pathway == "uti":
        urt_code = ["1090711000000102"]
        count_urt_6m = count_past_events(index_date, selected_events, urt_code, 6)
        count_urt_12m = count_past_events(index_date, selected_events, urt_code, 12)
        inclusion_criteria = (
            (age >= 16) & (age <= 64) & (patients.sex.is_in(["female"]))
        )
        exclusion_criteria = (
            pregnancy_status | (count_urt_6m >= 2) | (count_urt_12m >= 3)
        )

    elif clinical_pathway == "shingles":
        inclusion_criteria = age >= 18
        exclusion_criteria = pregnancy_status

    elif clinical_pathway == "impetigo":
        impetigo_code = ["48277006"]
        count_impetigo_12m = count_past_events(
            index_date, selected_events, impetigo_code, 12
        )
        inclusion_criteria = age >= 1
        exclusion_criteria = (count_impetigo_12m >= 2) | (pregnancy_status & (age < 16))

    elif clinical_pathway == "insect_bites":
        inclusion_criteria = age >= 1
        exclusion_criteria = pregnancy_status & (age < 16)

    elif clinical_pathway == "sore_throat":
        inclusion_criteria = age >= 5
        exclusion_criteria = pregnancy_status & (age < 16)

    elif clinical_pathway == "sinusitis":
        inclusion_criteria = age >= 12
        exclusion_criteria = pregnancy_status & (age < 16)

    elif clinical_pathway == "otitis_media":
        acute_otitis_code = ["3110003"]
        count_acute_otitis_6m = count_past_events(
            index_date, selected_events, acute_otitis_code, 6
        )
        count_acute_otitis_12m = count_past_events(
            index_date, selected_events, acute_otitis_code, 12
        )
        inclusion_criteria = (age >= 1) & (age <= 17)
        exclusion_criteria = (
            (count_acute_otitis_6m >= 3)
            | (count_acute_otitis_12m >= 4)
            | (pregnancy_status & (age < 16))
        )

    eligibility = (inclusion_criteria == True) & (exclusion_criteria == False)

    numerator_counts = (
        selected_events.where(selected_events.snomedct_code.is_in(condition_code))
        .where(eligibility)
        .exists_for_patient()
    )

    return numerator_counts


def get_age_band(patients, index_date):
    age = patients.age_on(index_date)
    age_band = case(
        when((age >= 0) & (age < 20)).then("0-19"),
        when((age >= 20) & (age < 40)).then("20-39"),
        when((age >= 40) & (age < 60)).then("40-59"),
        when((age >= 60) & (age < 80)).then("60-79"),
        when(age >= 80).then("80+"),
        when(age.is_null()).then("Missing"),
    )
    return age_band


def get_imd(addresses, index_date):
    imd_rounded = addresses.for_patient_on(index_date).imd_rounded
    max_imd = 32844
    imd_quintile = case(
        when((imd_rounded >= 0) & (imd_rounded < int(max_imd * 1 / 5))).then(
            "1 (Most Deprived)"
        ),
        when(imd_rounded < int(max_imd * 2 / 5)).then("2"),
        when(imd_rounded < int(max_imd * 3 / 5)).then("3"),
        when(imd_rounded < int(max_imd * 4 / 5)).then("4"),
        when(imd_rounded <= max_imd).then("5 (Least Deprived)"),
        otherwise="Missing",
    )
    return imd_quintile


def get_latest_ethnicity(
    index_date, clinical_events, ethnicity_codelist, ethnicity_from_sus, grouping=6
):
    latest_ethnicity_from_codes_category_num = (
        clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
        .where(clinical_events.date.is_on_or_before(index_date))
        .sort_by(clinical_events.date)
        .last_for_patient()
        .snomedct_code.to_category(ethnicity_codelist)
    )

    if grouping == 6:
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
            when(ethnicity_from_sus.code.is_in(["M", "N", "P"])).then(
                "Black or Black British"
            ),
            when(ethnicity_from_sus.code.is_in(["R", "S"])).then(
                "Chinese or Other Ethnic Groups"
            ),
        )
    elif grouping == 16:
        latest_ethnicity_from_codes = case(
            when(latest_ethnicity_from_codes_category_num == "1").then("White British"),
            when(latest_ethnicity_from_codes_category_num == "2").then("White Irish"),
            when(latest_ethnicity_from_codes_category_num == "3").then("Other White"),
            when(latest_ethnicity_from_codes_category_num == "4").then(
                "White and Caribbean"
            ),
            when(latest_ethnicity_from_codes_category_num == "5").then(
                "White and African"
            ),
            when(latest_ethnicity_from_codes_category_num == "6").then(
                "White and Asian"
            ),
            when(latest_ethnicity_from_codes_category_num == "7").then("Other Mixed"),
            when(latest_ethnicity_from_codes_category_num == "8").then("Indian"),
            when(latest_ethnicity_from_codes_category_num == "9").then("Pakistani"),
            when(latest_ethnicity_from_codes_category_num == "10").then("Bangladeshi"),
            when(latest_ethnicity_from_codes_category_num == "11").then(
                "Other South Asian"
            ),
            when(latest_ethnicity_from_codes_category_num == "12").then("Caribbean"),
            when(latest_ethnicity_from_codes_category_num == "13").then("African"),
            when(latest_ethnicity_from_codes_category_num == "14").then("Other Black"),
            when(latest_ethnicity_from_codes_category_num == "15").then("Chinese"),
            when(latest_ethnicity_from_codes_category_num == "16").then(
                "All other ethnic groups"
            ),
        )

        ethnicity_from_sus = case(
            when(ethnicity_from_sus.code == "A").then("White British"),
            when(ethnicity_from_sus.code == "B").then("White Irish"),
            when(ethnicity_from_sus.code == "C").then("Other White"),
            when(ethnicity_from_sus.code == "D").then("White and Caribbean"),
            when(ethnicity_from_sus.code == "E").then("White and African"),
            when(ethnicity_from_sus.code == "F").then("White and Asian"),
            when(ethnicity_from_sus.code == "G").then("Other Mixed"),
            when(ethnicity_from_sus.code == "H").then("Indian"),
            when(ethnicity_from_sus.code == "J").then("Pakistani"),
            when(ethnicity_from_sus.code == "K").then("Bangladeshi"),
            when(ethnicity_from_sus.code == "L").then("Other South Asian"),
            when(ethnicity_from_sus.code == "M").then("Caribbean"),
            when(ethnicity_from_sus.code == "N").then("African"),
            when(ethnicity_from_sus.code == "P").then("Other Black"),
            when(ethnicity_from_sus.code == "R").then("Chinese"),
            when(ethnicity_from_sus.code == "S").then("All other ethnic groups"),
        )

    ethnicity_combined = case(
        when(latest_ethnicity_from_codes.is_not_null()).then(
            latest_ethnicity_from_codes
        ),
        when(
            latest_ethnicity_from_codes.is_null() & ethnicity_from_sus.is_not_null()
        ).then(ethnicity_from_sus),
        otherwise="Missing",
    )

    return ethnicity_combined
