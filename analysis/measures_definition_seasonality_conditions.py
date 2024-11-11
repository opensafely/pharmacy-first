from ehrql import INTERVAL, create_measures, months
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    practice_registrations,
)
from measures_definition_pf_codes_conditions import pharmacy_first_conditions_codes

measures = create_measures()
measures.configure_dummy_data(population_size=1000)

start_date = "2023-01-01"
monthly_intervals = 22

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

for condition_name, condition_code in pharmacy_first_conditions_codes.items():
    condition_events = clinical_events.where(
        clinical_events.snomedct_code.is_in(condition_code)
    )

    # Define the numerator as the count of events for the condition
    numerator = condition_events.count_for_patient()
    denominator = registration.exists_for_patient() & patients.sex.is_in(["male", "female"])


    # Measures for overall clinical services graph
    measures.define_measure(
        name=f"countseasonality_{condition_name}",
        numerator=numerator,
        denominator=denominator,
        intervals=months(monthly_intervals).starting_on(start_date),
    )