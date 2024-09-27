from ehrql import INTERVAL, create_measures, months, codelist_from_csv, case, when
from ehrql.tables.tpp import clinical_events, practice_registrations, patients, addresses

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

# Import pharmacy first conditions codelist
pharmacy_first_conditions_codelist = codelist_from_csv(
    "codelists/user-chriswood-pharmacy-first-clinical-pathway-conditions.csv",
    column="code",
    category_column="term",
)

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

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
imd_quintile = case(
    when((imd >=0) & (imd < int(32844 * 1 / 5))).then("1 (most deprived)"),
    when(imd < int(32844 * 2 / 5)).then("2"),
    when(imd < int(32844 * 3 / 5)).then("3"),
    when(imd < int(32844 * 4 / 5)).then("4"),
    when(imd < int(32844 * 5 / 5)).then("5 (least deprived)"),
    otherwise="unknown"
)

# Select clinical events in interval date range
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
)

# Create measures for pharmacy first services
for pharmacy_first_event, codelist in pharmacy_first_event_codes.items():
    condition_events = selected_events.where(
        clinical_events.snomedct_code.is_in(codelist)
    )

    # Define the numerator as the count of events for the condition
    numerator = condition_events.count_for_patient()

    # Define the denominator as the number of patients registered
    denominator = registration.exists_for_patient()

    measures.define_measure(
        name=f"count_{pharmacy_first_event}",
        numerator=numerator,
        denominator=denominator,
        intervals=months(monthly_intervals).starting_on(start_date),
    )
    # Measures for age breakdown of clinical services
    measures.define_measure(
        name=f"count_{pharmacy_first_event}_by_age",
        numerator=numerator,
        denominator=denominator,
        group_by={
            "age_band": age_band,
        },
        intervals=months(monthly_intervals).starting_on(start_date),
    )

    # Measures for sex breakdown of clinical services
    measures.define_measure(
        name=f"count_{pharmacy_first_event}_by_sex",
        numerator=numerator,
        denominator=denominator,
        group_by={
            "sex": patients.sex,
        },
        intervals=months(monthly_intervals).starting_on(start_date),
    )

    # Measures for IMD breakdown of clinical services
    measures.define_measure(
        name=f"count_{pharmacy_first_event}_by_imd",
        numerator=numerator,
        denominator=denominator,
        group_by={
            "imd": imd_quintile,
        },
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

    # Define the denominator as the number of patients registered
    denominator = registration.exists_for_patient()

    measures.define_measure(
        name=f"count_{condition_name}",
        numerator=numerator,
        denominator=denominator,
        intervals=months(monthly_intervals).starting_on(start_date),
    )
    # Measures for age breakdown of clinical conditions
    measures.define_measure(
        name=f"count_{condition_name}_by_age",
        numerator=numerator,
        denominator=denominator,
        group_by={
            "age_band": age_band,
        },
        intervals=months(monthly_intervals).starting_on(start_date),
    )

    # Measures for age breakdown of clinical conditions
    measures.define_measure(
        name=f"count_{condition_name}_by_sex",
        numerator=numerator,
        denominator=denominator,
        group_by={
            "sex": patients.sex,
        },
        intervals=months(monthly_intervals).starting_on(start_date),
    )

    # Measures for imd breakdown of clinical conditions
    measures.define_measure(
        name=f"count_{condition_name}_by_imd",
        numerator=numerator,
        denominator=denominator,
        group_by={
            "imd": imd_quintile,
        },
        intervals=months(monthly_intervals).starting_on(start_date),
    )