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
from codelists import pharmacy_first_consultation_codelist
from config import start_date_measure_condition_provider, monthly_intervals_measure_condition_provider
from pf_variables_library import get_events_between, select_events_from_codelist

measures = create_measures()
measures.configure_dummy_data(population_size=1000)

start_date = start_date_measure_condition_provider
monthly_intervals = monthly_intervals_measure_condition_provider

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

selected_events = get_events_between(clinical_events, INTERVAL.start_date, INTERVAL.end_date)

# Create variable which contains boolean values of whether pharmacy first event exists for patient
has_pharmacy_first = select_events_from_codelist(selected_events, pharmacy_first_consultation_codelist).exists_for_patient()

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