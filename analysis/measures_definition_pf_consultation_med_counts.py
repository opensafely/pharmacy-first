from ehrql import INTERVAL, create_measures, months
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    practice_registrations,
)
from ehrql.tables.raw.tpp import medications

from config import start_date_measure_med_counts, monthly_intervals_measure_med_counts
from codelists import (
    pf_consultation_events_dict,
    pf_med_codelist,
)
from pf_variables_library import select_events

# Script taken from Pharmacy First Data Development (for top 10 PF meds table)

measures = create_measures()
measures.configure_dummy_data(population_size=1000)

start_date = start_date_measure_med_counts
monthly_intervals = monthly_intervals_measure_med_counts

registration = practice_registrations.for_patient_on(INTERVAL.end_date)

# Select Pharmacy First events during interval date range
pharmacy_first_events = select_events(
    clinical_events, start_date=INTERVAL.start_date, end_date=INTERVAL.end_date
).where(
    clinical_events.snomedct_code.is_in(
        pf_consultation_events_dict["pf_consultation_services_combined"]
    )
)

pharmacy_first_ids = pharmacy_first_events.consultation_id
has_pf_consultation = pharmacy_first_events.exists_for_patient()

# Select Pharmacy First consultations during interval date range
selected_medications = select_events(
    medications, start_date=INTERVAL.start_date, end_date=INTERVAL.end_date
).where(medications.consultation_id.is_in(pharmacy_first_ids))

# First medication for each patient
first_selected_medication = (
    selected_medications.sort_by(selected_medications.date).first_for_patient().dmd_code
)
# Boolean variable that selected medication is part of pharmacy first med codelists
has_pharmacy_first_medication = first_selected_medication.is_in(pf_med_codelist)

# Numerator, patients with a PF medication
# This allows me to count all (first) medications linked to a PF consultation
numerator = first_selected_medication.is_not_null()

# Denominator, registered patients (f/m) with a PF consultation
denominator = (
    registration.exists_for_patient()
    & patients.sex.is_in(["male", "female"])
    & has_pf_consultation
)

measures.define_measure(
    name="pf_medication_count",
    numerator=first_selected_medication.is_not_null(),
    denominator=denominator,
    group_by={
        "dmd_code": first_selected_medication,
        "pharmacy_first_med": has_pharmacy_first_medication,
    },
    intervals=months(monthly_intervals).starting_on(start_date),
)
