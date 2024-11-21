from ehrql import INTERVAL, create_measures, months
from ehrql.tables.tpp import (
    practice_registrations,
    patients,
)

from pf_dataset import pharmacy_first_event_codes
from measures_definition_pf_medications import pharmacy_first_med_codes
from measures_definition_pf_breakdown import pharmacy_first_conditions_codes, selected_events

measures = create_measures()
measures.configure_dummy_data(population_size=1000)

start_date = "2024-02-01"
monthly_intervals = 9

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

# Loop through all codes in each sublist of the dictionary to flatten the list ready for is_in commands to be used and have a list of pf_condition codes
pf_condition_codelist = [code for sublist in pharmacy_first_conditions_codes.values() for code in sublist]

# Create variable which contains boolean values of whether pharmacy first event exists for patient
has_pf_consultation = selected_events.where(
    selected_events.snomedct_code.is_in(
        pharmacy_first_event_codes["combined_pf_service"]
    )
).exists_for_patient()

# PF consultations with PF clinical condition
has_pf_condition = selected_events.where(
    selected_events.snomedct_code.is_in(
        pf_condition_codelist
    )
).exists_for_patient()

# PF consultations with prescribed PF medication
has_pf_medication = selected_events.where(
    selected_events.snomedct_code.is_in(
        pharmacy_first_med_codes
    )
).exists_for_patient()

# Define the denominator as the number of patients registered
denominator = registration.exists_for_patient() & patients.sex.is_in(["male", "female"]) & has_pf_consultation
measures.define_defaults(
    denominator = denominator)

# Measures for PF consultations with PF medication
measures.define_measure(
    name="count_pfmed_status",
    numerator=has_pf_medication,
    intervals=months(monthly_intervals).starting_on(start_date),
)
# Measures for PF consultations with PF condition
measures.define_measure(
    name="count_pfcondition_status",
    numerator=has_pf_condition,
    intervals=months(monthly_intervals).starting_on(start_date),
)

# Measures for PF consultations with both PF medication and condition
measures.define_measure(
    name="count_pfmed_and_pfcondition_status",
    numerator=has_pf_condition & has_pf_medication,
    intervals=months(monthly_intervals).starting_on(start_date),
)
