from ehrql import INTERVAL, create_measures, months, codelist_from_csv
from ehrql.tables.tpp import clinical_events, patients, practice_registrations

measures = create_measures()

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

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

# Select clinical events in interval date range
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
)

# Loop through each condition to create a measure
for condition_name, codelist in pharmacy_first_event_codes.items():
    condition_events = selected_events.where(
        clinical_events.snomedct_code.is_in(codelist)
    )

    # Define the numerator as the count of events for the condition
    numerator = condition_events.count_for_patient()


    # Define the denominator as the number of patients registered
    denominator = registration.exists_for_patient()

    # Define the measure
    measures.define_measure(
        name=f"count_{condition_name}",
        numerator=numerator,
        denominator=denominator,
        intervals=months(8).starting_on("2023-11-01")
    )

measures.configure_dummy_data(population_size=1000)

# # Count pharmacy first codes
# pharmacy_first_code_counts = {}

# for code_desc, code in pharmacy_first_event_codes.items():
#     count_codes_query = selected_events.where(
#         selected_events.snomedct_code.is_in(code)
#     ).count_for_patient()
#     pharmacy_first_code_counts[f"count_{code_desc}"] = count_codes_query


# for measures_name, code_counts in pharmacy_first_code_counts.items():
#     measures.define_measure(
#         name=measures_name,
#         numerator=code_counts,
#         group_by={
#             "practice_region": registration.practice_nuts1_region_name
#             },
#         denominator=patients.exists_for_patient(),
#         intervals=intervals,
#     )

    