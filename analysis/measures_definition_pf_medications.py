from ehrql import INTERVAL, create_measures, months
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    practice_registrations,
)
from ehrql.tables.raw.tpp import medications

from pf_dataset import pharmacy_first_event_codes

measures = create_measures()
measures.configure_dummy_data(population_size=1000)

start_date = "2023-11-01"
monthly_intervals = 9

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

# Select Pharmacy First events during interval date range
pharmacy_first_events = clinical_events.where(
    clinical_events.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
).where(
    clinical_events.snomedct_code.is_in(
        pharmacy_first_event_codes["combined_pf_service"]
    )
)

pharmacy_first_ids = pharmacy_first_events.consultation_id
has_pharmacy_first_consultation = pharmacy_first_events.exists_for_patient()

# Select Pharmacy First medications during interval date range
pharmacy_first_medications = medications.where(
    medications.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
).where(medications.consultation_id.is_in(pharmacy_first_ids))

first_pharmacy_first_medication = (
    pharmacy_first_medications.sort_by(medications.date).first_for_patient().dmd_code
)
has_pharmacy_first_medication = pharmacy_first_medications.exists_for_patient()

# Numerator, patients with a PF medication
# This allows me to count all (first) medications linked to a PF consultation
numerator = has_pharmacy_first_medication

# Denominator, registered patients (f/m) with a PF consultation
denominator = (
    registration.exists_for_patient()
    & patients.sex.is_in(["male", "female"])
    & has_pharmacy_first_consultation
)

measures.define_measure(
    name="pf_medication_count",
    numerator=has_pharmacy_first_medication,
    denominator=denominator,
    group_by={
        "dmd_code": first_pharmacy_first_medication,
    },
    intervals=months(monthly_intervals).starting_on(start_date),
)
