from ehrql import INTERVAL, create_measures, months, case, when
from ehrql.tables.tpp import (
    clinical_events,
    practice_registrations,
    patients,
    addresses,
    ethnicity_from_sus,
)
from codelists import pharmacy_first_conditions_codelist, ethnicity_codelist, pregnancy_codelist

measures = create_measures()
measures.configure_dummy_data(population_size=1000)

start_date = "2023-11-01"
monthly_intervals = 9

# Create dictionary of pharmacy first codes
pharmacy_first_event_codes = {
    # Community Pharmacy (CP) Blood Pressure (BP) Check Service (procedure)
    "blood_pressure_service": ["1659111000000107"],
    # Community Pharmacy (CP) Contraception Service (procedure)
    "contraception_service": ["1659121000000101"],
    # Community Pharmacist (CP) Consultation Service for minor illness (procedure)
    "consultation_service": ["1577041000000109"],
    # Pharmacy First service (qualifier value)
    "pharmacy_first_service": ["983341000000102"],
}

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

latest_ethnicity_from_codes_category_num = (
    clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
    .where(clinical_events.date.is_on_or_before(INTERVAL.start_date))
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


# Age bands for age breakdown
age = patients.age_on(INTERVAL.start_date)
age_band = case(
    when((age >= 0) & (age < 20)).then("0-19"),
    when((age >= 20) & (age < 40)).then("20-39"),
    when((age >= 40) & (age < 60)).then("40-59"),
    when((age >= 60) & (age < 80)).then("60-79"),
    when(age >= 80).then("80+"),
    when(age.is_null()).then("Missing"),
)

# IMD groupings for IMD breakdown
imd = addresses.for_patient_on(INTERVAL.start_date).imd_rounded
max_imd = 32844
imd_quintile = case(
    when((imd >= 0) & (imd < int(max_imd * 1 / 5))).then("1 (Most Deprived)"),
    when(imd < int(max_imd * 2 / 5)).then("2"),
    when(imd < int(max_imd * 3 / 5)).then("3"),
    when(imd < int(max_imd * 4 / 5)).then("4"),
    when(imd <= max_imd).then("5 (Least Deprived)"),
    otherwise="Missing",
)

latest_region = case(
    when(
        registration.practice_nuts1_region_name.is_not_null()
    ).then(registration.practice_nuts1_region_name),
    otherwise="Missing",
)

# Create variable which when not null, indicates patient is pregnant
pregnancy_status = (
    clinical_events.where(clinical_events.snomedct_code.is_in(pregnancy_codelist))
    .where(clinical_events.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .date
)

# Create function to count number of diagnosis of a condition, and the length of time window
def condition_history(condition_code, month):
    return (
        clinical_events.where(clinical_events.snomedct_code.is_in(condition_code))
        .where(clinical_events.date.is_on_or_between(INTERVAL.start_date - months(month), INTERVAL.start_date))
        .count_for_patient()
    )

# Call function to create variables which contain the number of repeated diagnoses
urt_code = ["1090711000000102"]
impetigo_code = ["48277006"]
acute_sinusitis_code = ["15805002"]
acute_otitis_code = ["3110003"]
urt_6m = condition_history(urt_code, 6)
urt_12m = condition_history(urt_code, 12)
impetigo_12m = condition_history(impetigo_code, 12)
acute_otitis_6m = condition_history(acute_otitis_code, 6)
acute_otitis_12m = condition_history(acute_otitis_code, 12)

# Select clinical events in interval date range
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
)

# Breakdown metrics to be produced as graphs
breakdown_metrics = {
    "age_band": age_band,
    "sex": patients.sex,
    "imd": imd_quintile,
    "region": latest_region,
    "ethnicity": ethnicity_combined,
}

# Define the denominator as the number of patients registered
denominator = registration.exists_for_patient() & patients.sex.is_in(["male", "female"])

# Create measures for pharmacy first services
for pharmacy_first_event, codelist in pharmacy_first_event_codes.items():
    condition_events = selected_events.where(
        clinical_events.snomedct_code.is_in(codelist)
    )

    # Define the numerator as the count of events for the condition
    numerator = condition_events.count_for_patient()

    # Measures for overall clinical services graph
    measures.define_measure(
        name=f"count_{pharmacy_first_event}",
        numerator=numerator,
        denominator=denominator,
        intervals=months(monthly_intervals).starting_on(start_date),
    )

    # Nested loop for each breakdown measure in clinical services
    for breakdown, variable in breakdown_metrics.items():
        measures.define_measure(
            name=f"count_{pharmacy_first_event}_by_{breakdown}",
            numerator=numerator,
            denominator=denominator,
            group_by={breakdown: variable},
            intervals=months(monthly_intervals).starting_on(start_date),
        )

# Create denominator variables for each clinical condition based on NHS England rules using sex, age, pregnancy status and repeated diagnoses
# The following exclusions have not been added: urinary catheter for URT, bullous impetigo, chronic sinusitis and immunosuppressed individuals for acute sinusitis 
denominator_uncomplicated_uti = (age>=16) & (age<=64) & (patients.sex.is_in(["female"]) & pregnancy_status.is_null()) | (urt_6m<2) | (urt_12m<3)
denominator_shingles = (age>=18) & pregnancy_status.is_null()
denominator_impetigo = (age>=1) | (pregnancy_status.is_not_null() & (age>=16)) | (impetigo_12m<2)
denominator_infected_insect_bites = (age>=1) | (pregnancy_status.is_not_null() & (age>=16))
denominator_acute_sore_throat = (age>=5) | (pregnancy_status.is_not_null() & (age>=16))
denominator_acute_sinusitis = (age>=12) | (pregnancy_status.is_not_null() & (age>=16))
denominator_acute_otitis_media = (age>=1) & (age<=17) | (pregnancy_status.is_not_null() & (age>=16)) |(acute_otitis_6m<3) | (acute_otitis_12m<4)

# Create dictionary for clinical condition denominators
pf_condition_denominators = {
    "uncomplicated_urinary_tract_infection" : denominator_uncomplicated_uti,
    "herpes_zoster" : denominator_shingles,
    "impetigo" : denominator_impetigo,
    "infected_insect_bite": denominator_infected_insect_bites,
    "acute_pharyngitis" : denominator_acute_sore_throat,
    "acute_sinusitis" : denominator_acute_sinusitis,
    "acute_otitis_media" : denominator_acute_otitis_media,
}

# Create measures for pharmacy first conditions
pharmacy_first_conditions_codes = {}
for codes, term in pharmacy_first_conditions_codelist.items():
    normalised_term = term.lower().replace(" ", "_")
    codes = [codes]
    pharmacy_first_conditions_codes[normalised_term] = codes

for condition_name, condition_code in pharmacy_first_conditions_codes.items():
    condition_events = selected_events.where(
        clinical_events.snomedct_code.is_in(condition_code)
    )

    # Define the numerator as the count of events for the condition
    numerator = condition_events.count_for_patient()

    # Measures for overall clinical services graph
    measures.define_measure(
        name=f"count_{condition_name}",
        numerator=numerator,
        denominator=pf_condition_denominators[condition_name],
        intervals=months(monthly_intervals).starting_on(start_date),
    )

    # Nested loop for each breakdown measure in clinical conditions
    for breakdown, variable in breakdown_metrics.items():
        measures.define_measure(
            name=f"count_{condition_name}_by_{breakdown}",
            numerator=numerator,
            denominator=pf_condition_denominators[condition_name],
            group_by={breakdown: variable},
            intervals=months(monthly_intervals).starting_on(start_date),
        )
