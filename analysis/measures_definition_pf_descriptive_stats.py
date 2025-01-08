from ehrql import INTERVAL, create_measures, months
from ehrql.tables.raw.tpp import medications
from ehrql.tables.tpp import practice_registrations, patients, clinical_events

from pf_variables_library import select_events
from codelists import (
    pharmacy_first_med_codelist,
    pharmacy_first_consultation_codelist,
    pharmacy_first_conditions_codelist,
)
from config import (
    start_date_measure_descriptive_stats,
    monthly_intervals_measure_descriptive_stats,
)

measures = create_measures()
measures.configure_dummy_data(population_size=100)
measures.configure_disclosure_control(enabled=True)

start_date = start_date_measure_descriptive_stats
monthly_intervals = monthly_intervals_measure_descriptive_stats

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

# Select clinical events and medications for measures INTERVAL
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(
        INTERVAL.start_date,
        INTERVAL.end_date,
    )
)
selected_medications = medications.where(
    medications.date.is_on_or_between(
        INTERVAL.start_date,
        INTERVAL.end_date,
    )
)

# Select all Pharmacy First consultation events
pf_consultation_events = select_events(
    selected_events,
    codelist=pharmacy_first_consultation_codelist,
)

# Extract Pharmacy First consultation IDs and dates
pf_ids = pf_consultation_events.consultation_id
pf_dates = pf_consultation_events.date

has_pf_consultation = pf_consultation_events.exists_for_patient()

# Select Pharmacy First conditions by ID and date
selected_pf_id_conditions = selected_events.where(
    selected_events.consultation_id.is_in(pf_ids)
).where(selected_events.snomedct_code.is_in(pharmacy_first_conditions_codelist))

selected_pf_date_conditions = (
    selected_events.where(selected_events.consultation_id.is_not_in(pf_ids))
    .where(selected_events.date.is_in(pf_dates))
    .where(selected_events.snomedct_code.is_in(pharmacy_first_conditions_codelist))
)

has_pf_id_condition = selected_pf_id_conditions.exists_for_patient()
has_pf_date_condition = selected_pf_date_conditions.exists_for_patient()

# Select Pharmacy First Medications by ID and date
selected_pf_id_medications = selected_medications.where(
    selected_medications.consultation_id.is_in(pf_ids)
).where(selected_medications.dmd_code.is_in(pharmacy_first_med_codelist))

selected_pf_date_medications = (
    selected_medications.where(selected_medications.consultation_id.is_not_in(pf_ids))
    .where(selected_medications.date.is_in(pf_dates))
    .where(selected_medications.dmd_code.is_in(pharmacy_first_med_codelist))
)

has_pf_id_medication = selected_pf_id_medications.exists_for_patient()
has_pf_date_medication = selected_pf_date_medications.exists_for_patient()

# Define measures
measures.define_defaults(
    denominator=(
        registration.exists_for_patient()
        & patients.sex.is_in(["male", "female"])
        & has_pf_consultation
    ),
    intervals=months(monthly_intervals).starting_on(start_date),
)

# Measures linked by Pharmacy First consultation ID
measures.define_measure(
    name="pfmed_with_pfid",
    numerator=has_pf_id_medication,
)

measures.define_measure(
    name="pfcondition_with_pfid",
    numerator=has_pf_id_condition,
)

measures.define_measure(
    name="pfmed_and_pfcondition_with_pfid",
    numerator=has_pf_id_medication & has_pf_id_condition,
)

# Measures linked by Pharmacy First consultation date
measures.define_measure(
    name="pfmed_on_pfdate",
    numerator=has_pf_date_medication,
)

measures.define_measure(
    name="pfcondition_on_pfdate",
    numerator=has_pf_date_condition,
)

measures.define_measure(
    name="pfmed_and_pfcondition_on_pfdate",
    numerator=has_pf_date_medication & has_pf_date_condition,
)
