from ehrql import INTERVAL, create_measures, months
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    practice_registrations,
)
from analysis.measures_definition_pf_breakdown import (
    pharmacy_first_conditions_codes,
    imd_quintile,
)
from pf_dataset import pharmacy_first_event_codes


measures = create_measures()
measures.configure_dummy_data(population_size=1000)

start_date = "2023-01-01"
monthly_intervals = 22

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(INTERVAL.start_date, INTERVAL. end_date)
)

# Create variable which contains boolean values of whether pharmacy first event exists for patient
has_pharmacy_first = selected_events.where(
    selected_events.snomedct_code.is_in(
        pharmacy_first_event_codes["combined_pf_service"]
    )
).exists_for_patient()

for condition_name, condition_code in pharmacy_first_conditions_codes.items():
    condition_events = selected_events.where(
        selected_events.snomedct_code.is_in(condition_code)
    )

    # Define the numerator as the count of events for the condition
    numerator = condition_events.count_for_patient()
    denominator = registration.exists_for_patient() & patients.sex.is_in(["male", "female"])

    # Measures for overall clinical services graph
    measures.define_measure(
        name=f"count_{condition_name}_total",
        numerator=numerator,
        denominator=denominator,
        group_by={
            "pf_status": has_pharmacy_first,
            "imd": imd_quintile
        },
        intervals=months(monthly_intervals).starting_on(start_date),
    )