from ehrql import INTERVAL, create_measures, months
from ehrql.tables.tpp import (
    clinical_events,
    practice_registrations,
    patients,
    addresses,
)

from codelists import pf_consultation_events_dict
from config import start_date_measure_pf_breakdown, monthly_intervals_measure_pf_breakdown
from pf_variables_library import select_events

measures = create_measures()
measures.configure_dummy_data(population_size=1000)

start_date = start_date_measure_pf_breakdown
monthly_intervals = monthly_intervals_measure_pf_breakdown

registration = practice_registrations.for_patient_on(INTERVAL.end_date)
msoa_code = addresses.for_patient_on(INTERVAL.start_date).msoa_code
pharmacy_first_ids = select_events(clinical_events, codelist=pf_consultation_events_dict["pf_consultation_services_combined"]).consultation_id
# # Select clinical events in interval date range
selected_events = select_events(clinical_events, start_date=INTERVAL.start_date, end_date=INTERVAL.end_date).where(
    clinical_events.consultation_id.is_in(pharmacy_first_ids)
)

# Define the denominator as the number of patients registered
denominator = registration.exists_for_patient() & patients.sex.is_in(["male", "female"])

condition_events = select_events(select_events, codelist=pf_consultation_events_dict["pf_consultation_services_combined"])
numerator = condition_events.count_for_patient()

measures.define_measure(
    name="count_pf_consultation_services_by_msoa",
    numerator=numerator,
    denominator=denominator,
    group_by=msoa_code,
    intervals=months(monthly_intervals).starting_on(start_date),
)
