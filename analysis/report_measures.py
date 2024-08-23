from ehrql import INTERVAL, create_measures, months, codelist_from_csv
from ehrql.tables.tpp import clinical_events, patients, practice_registrations

measures = create_measures()
measures.configure_dummy_data(population_size=1000)

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
# The following codes come from codelists/user-chriswood-pharmacy-first-clinical-pathway-conditions.csv file.
# Currently written as a hardcoded dictionary to allow for easy for looping (ln66-83), but will be imported from codelist csv in future commits.
# Pharmacy First seven clinical conditions codelist
pharmacy_first_conditions_codes = {
    # Community Pharmacy (CP) Blood Pressure (BP) Check Service (procedure)
    "acute_otitis_media": ["3110003"],
    # Community Pharmacy (CP) Contraception Service (procedure)
    "herpes_zoster": ["4740000"],
    # Community Pharmacist (CP) Consultation Service for minor illness (procedure)
    "acute_sinusitis": ["15805002"],
    # Pharmacy First service (qualifier value)
    "impetigo": ["48277006"],
    # Community Pharmacy (CP) Contraception Service (procedure)
    "infected_insect_bite": ["262550002"],
    # Community Pharmacist (CP) Consultation Service for minor illness (procedure)
    "acute_pharyngitis": ["363746003"],
    # Pharmacy First service (qualifier value)
    "uncomplicated_urinary_tract_infection": ["1090711000000102"],
}

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

# Select clinical events in interval date range
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
)

# Loop through each condition to create a measure
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
        intervals=months(8).starting_on("2023-11-01")
    )

# Loop through each CLINICAL condition to create a measure
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
        intervals=months(8).starting_on("2023-11-01")
    )