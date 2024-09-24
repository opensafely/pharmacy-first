from ehrql import INTERVAL, create_measures, months, codelist_from_csv
from ehrql.tables.tpp import clinical_events, patients, practice_registrations

measures = create_measures()
measures.configure_dummy_data(population_size=1000)

start_date = "2023-11-01"
monthly_intervals = 8

# Dictionary of pharmacy first codes
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

# Import the codelist from CSV
pharmacy_first_conditions_codelist = codelist_from_csv(
    "codelists/user-chriswood-pharmacy-first-clinical-pathway-conditions.csv",
    column="code",
    category_column="term",
)

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

# Select clinical events in interval date range
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
)

# Iterate through codelist, forming a dictionary
pharmacy_first_conditions_codes = {}
for codes, term in pharmacy_first_conditions_codelist.items():
    normalised_term = term.lower().replace(" ", "_")
    codes = [codes]
    pharmacy_first_conditions_codes[normalised_term] = codes

# Loop through each CLINICAL SERVICE to create a measure
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

# Loop through each CLINICAL CONDITION to create a measure
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
