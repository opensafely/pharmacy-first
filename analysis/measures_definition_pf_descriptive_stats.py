from ehrql import INTERVAL, create_measures, months
from ehrql.tables.raw.tpp import medications
from ehrql.tables.tpp import practice_registrations, patients, clinical_events

from pf_variables_library import select_events
from codelists import (
    pharmacy_first_med_codelist,
    pharmacy_first_consultation_codelist,
    pharmacy_first_conditions_codelist,
)
from config import start_date_measure_descriptive_stats, monthly_intervals_measure_descriptive_stats

measures = create_measures()
measures.configure_dummy_data(population_size=1000)
measures.configure_disclosure_control(enabled=True)

start_date = start_date_measure_descriptive_stats
monthly_intervals = monthly_intervals_measure_descriptive_stats

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

# Function to retrieve consultation ids from clinical events that are PF consultations
pharmacy_first_ids = select_events(
    clinical_events, codelist=pharmacy_first_consultation_codelist
).consultation_id

# Function to retrieve selected events using pharmacy first ids
selected_clinical_events = select_events(
    clinical_events, consultation_ids=pharmacy_first_ids
).where(clinical_events.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date))

selected_med_events = select_events(
    medications, consultation_ids=pharmacy_first_ids).where(
    medications.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
)

# Create variable which contains boolean values of whether pharmacy first event exists for patient
has_pf_consultation = select_events(
    selected_clinical_events, codelist=pharmacy_first_consultation_codelist).exists_for_patient()

# PF consultations with PF clinical condition
has_pf_condition = select_events(
    selected_clinical_events, codelist=pharmacy_first_conditions_codelist).exists_for_patient()

# Dates of pharmacy first consultations
pharmacy_first_dates = select_events(clinical_events, codelist=pharmacy_first_ids).date

# Specify whether a patient has been prescribed a PF medication on the same day as a PF consultation code
has_pfmed_on_pfdate = selected_med_events.where(medications.date.is_in(pharmacy_first_dates))

# Specify whether a patient has a PF condition
has_pfpathway_on_pfdate = has_pf_condition.where(
    has_pf_condition.date.is_in(pharmacy_first_dates)
)

# PF consultations with prescribed PF medication
has_pf_medication = selected_med_events.where(
    selected_med_events.dmd_code.is_in(pharmacy_first_med_codelist)
).exists_for_patient()

# Define the denominator as the number of patients registered
denominator = (
    registration.exists_for_patient()
    & patients.sex.is_in(["male", "female"])
    & has_pf_consultation
)
measures.define_defaults(denominator=denominator)

# Denominator without the pf_consultation constraint
study_population = (
    registration.exists_for_patient()
    & patients.sex.is_in(["male", "female"])
)

# Measures for PF consultations with PF medication
measures.define_measure(
    name="pf_with_pfmed",
    numerator=has_pf_medication,
    intervals=months(monthly_intervals).starting_on(start_date),
)
# Measures for PF consultations with PF condition
measures.define_measure(
    name="pf_with_pfcondition",
    numerator=has_pf_condition,
    intervals=months(monthly_intervals).starting_on(start_date),
)

# Measures for PF consultations with both PF medication and condition
measures.define_measure(
    name="pf_with_pfmed_and_pfcondition",
    numerator=has_pf_condition & has_pf_medication,
    intervals=months(monthly_intervals).starting_on(start_date),
)

# Measures for PF medications prescribed on the same day as PF consultation 
measures.define_measure(
    name="pfmed_on_pfdate",
    numerator=has_pfmed_on_pfdate,
    denominator=study_population,
    intervals=months(monthly_intervals).starting_on(start_date),
)

# Measures for PF conditions diagnosed on the same day as PF consultation 
measures.define_measure(
    name="pfpathway_on_pfdate",
    numerator=has_pfpathway_on_pfdate,
    denominator=study_population,
    intervals=months(monthly_intervals).starting_on(start_date),
)

# Measures for PF conditions diagnosed and PF med prescribed on the same day as PF consultation 
measures.define_measure(
    name="pfmed_and_pfpathway_on_pfdate",
    numerator=has_pfmed_on_pfdate & has_pfpathway_on_pfdate,
    denominator=study_population,
    intervals=months(monthly_intervals).starting_on(start_date),
)
