from ehrql import INTERVAL, create_measures, months, case, when
from ehrql.tables.tpp import (
    clinical_events,
    practice_registrations,
    patients,
    addresses,
)
from codelists import pharmacy_first_conditions_codelist, ethnicity_codelist

measures = create_measures()
measures.configure_dummy_data(population_size=1000)

start_date = "2023-11-01"
monthly_intervals = 8

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

latest_ethnicity_category_num = (
    clinical_events.where(clinical_events.snomedct_code.is_in(ethnicity_codelist))
    .where(clinical_events.date.is_on_or_before(INTERVAL.start_date))
    .sort_by(clinical_events.date)
    .last_for_patient()
    .snomedct_code.to_category(ethnicity_codelist)
)

latest_ethnicity_category_desc = case(
    when(latest_ethnicity_category_num == "1").then("White"),
    when(latest_ethnicity_category_num == "2").then("Mixed"),
    when(latest_ethnicity_category_num == "3").then("Asian or Asian British"),
    when(latest_ethnicity_category_num == "4").then("Black or Black British"),
    when(latest_ethnicity_category_num == "5").then("Chinese or Other Ethnic Groups"),
    when(latest_ethnicity_category_num.is_null()).then("Missing"),
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
    ).registration.practice_nuts1_region_name,
    otherwise="Missing",
)

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
    "ethnicity": latest_ethnicity_category_desc,
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
        denominator=denominator,
        intervals=months(monthly_intervals).starting_on(start_date),
    )

    # Nested loop for each breakdown measure in clinical conditions
    for breakdown, variable in breakdown_metrics.items():
        measures.define_measure(
            name=f"count_{condition_name}_by_{breakdown}",
            numerator=numerator,
            denominator=denominator,
            group_by={breakdown: variable},
            intervals=months(monthly_intervals).starting_on(start_date),
        )
