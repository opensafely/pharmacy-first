from ehrql import INTERVAL, create_measures, months
from ehrql.tables.raw.tpp import medications
from ehrql.tables.tpp import (
    practice_registrations,
    patients,
    clinical_events
)

from pf_codelist_functions import *
from codelists import pharmacy_first_med_codes, pharmacy_first_consultations_codelist, pharmacy_first_conditions_codelist

measures = create_measures()
measures.configure_dummy_data(population_size=1000)
#measures.configure_disclosure_control(enabled=False)

start_date = "2024-02-01"
monthly_intervals = 9

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

# Function to call pf_condition_codelist
pf_conditions_codes = get_pf_condition_codes(pharmacy_first_conditions_codelist)

# Function to retrieve consultation ids from clinical events that are PF consultations
pharmacy_first_ids = get_consultation_ids(clinical_events, pharmacy_first_consultations_codelist)

# Function to retrieve selected events using pharmacy first ids
selected_events = get_selected_events(clinical_events, pharmacy_first_ids, INTERVAL)
med_events = get_selected_events(medications, pharmacy_first_ids, INTERVAL)

# Create variable which contains boolean values of whether pharmacy first event exists for patient
has_pf_consultation = selected_events.where(
    selected_events.snomedct_code.is_in(
        pharmacy_first_consultations_codelist

    )
).exists_for_patient()

# PF consultations with PF clinical condition
has_pf_condition = selected_events.where(
    selected_events.snomedct_code.is_in(
        pf_conditions_codes
    )
).exists_for_patient()

# PF consultations with prescribed PF medication
has_pf_medication = med_events.where(
    med_events.dmd_code.is_in(
        pharmacy_first_med_codes
    )
).exists_for_patient()

# Define the denominator as the number of patients registered
denominator = registration.exists_for_patient() & patients.sex.is_in(["male", "female"]) & has_pf_consultation
measures.define_defaults(
    denominator = denominator)

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
