from ehrql import INTERVAL, create_measures, months
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    practice_registrations,
)
from ehrql.tables.raw.tpp import medications
from codelists import *

measures = create_measures()
measures.configure_dummy_data(population_size=1000)
# Turn off during code development, but turn on before running against on the server
measures.configure_disclosure_control(enabled=True)

start_date = "2023-11-01"
monthly_intervals = 9

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

# Select Pharmacy First consultations during interval date range
pharmacy_first_events = clinical_events.where(
    clinical_events.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
).where(
    clinical_events.snomedct_code.is_in(
        pharmacy_first_consultation_codelist
    )
)

pharmacy_first_ids = pharmacy_first_events.consultation_id
has_pharmacy_first_consultation = pharmacy_first_events.exists_for_patient()

# Select medications prescribed with PF consultation ID
selected_medications = medications.where(
    medications.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
).where(medications.consultation_id.is_in(pharmacy_first_ids))

# Select first medication for group_by argument in measures
first_selected_medication = (
    selected_medications.sort_by(medications.date).first_for_patient().dmd_code
)

# Check if a medication is from our PF codelists 
has_pharmacy_first_medication = first_selected_medication.is_in(
    pharmacy_first_med_codelist
)

# Numerator, patients with a PF medication
# This allows me to count all (first) medications linked to a PF consultation
numerator = has_pharmacy_first_medication

# Denominator, registered patients (f/m) with a PF consultation
denominator = (
    registration.exists_for_patient()
    & patients.sex.is_in(["male", "female"])
    & has_pharmacy_first_medication
)

measures.define_measure(
    name="pf_medication_count",
    numerator=has_pharmacy_first_medication,
    denominator=denominator,
    group_by={
        "dmd_code": first_selected_medication
    },
    intervals=months(monthly_intervals).starting_on(start_date),
)
