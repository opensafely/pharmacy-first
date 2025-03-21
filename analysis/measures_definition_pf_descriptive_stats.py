from ehrql import INTERVAL, create_measures, months
from ehrql.tables.raw.tpp import medications
from ehrql.tables.tpp import practice_registrations, patients, clinical_events

from pf_variables_library import select_events
from codelists import (
    pf_med_codelist,
    pf_consultation_events_dict,
    pf_conditions_codelist,
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
    codelist=pf_consultation_events_dict["pf_consultation_services_combined"],
)

# Extract Pharmacy First consultation IDs
pf_ids = pf_consultation_events.consultation_id
has_pf_consultation = pf_consultation_events.exists_for_patient()

# Counts number of Pharmacy First consultations
pf_consultation_count = pf_consultation_events.count_for_patient()


# Pharmacy First conditions
selected_pf_id_conditions = selected_events.where(
    selected_events.consultation_id.is_in(pf_ids)
).where(selected_events.snomedct_code.is_in(pf_conditions_codelist))

selected_pf_id_condition_ids = selected_pf_id_conditions.consultation_id

selected_pf_id_non_pf_events = (
    selected_events.where(selected_events.consultation_id.is_in(pf_ids))
    .except_where(selected_events.snomedct_code.is_in(pf_conditions_codelist))
    .except_where(
        selected_events.snomedct_code.is_in(
            pf_consultation_events_dict["pf_consultation_services_combined"]
        )
    )
)

# Counts all other clinical events linked to PF ID per month
nonpf_event_count = selected_pf_id_non_pf_events.count_for_patient()

# Pharmacy First medications
selected_pf_id_medications = selected_medications.where(
    selected_medications.consultation_id.is_in(pf_ids)
).where(selected_medications.dmd_code.is_in(pf_med_codelist))

selected_pf_id_medication_ids = selected_pf_id_medications.consultation_id

selected_pf_id_non_pf_medications = selected_medications.where(
    selected_medications.consultation_id.is_in(pf_ids)
).except_where(selected_medications.dmd_code.is_in(pf_med_codelist))

# Counts all other medications linked to PF ID per month
nonpf_med_count = (
    selected_pf_id_non_pf_medications.consultation_id.count_distinct_for_patient()
)

# Count PF consultations linked to (1) PF MED ONLY (2) PF CONDITION ONLY (3) BOTH
# (1) PF MED ONLY
count_pf_med_only = selected_pf_id_medications.where(
    selected_pf_id_medications.consultation_id.is_not_in(selected_pf_id_condition_ids)
).consultation_id.count_distinct_for_patient()

# (2) PF CONDITION
count_pf_condition_only = selected_pf_id_conditions.where(
    selected_pf_id_conditions.consultation_id.is_not_in(selected_pf_id_medication_ids)
).consultation_id.count_distinct_for_patient()

# (3) BOTH, these should give us identical numbers
count_pf_both = selected_pf_id_medications.where(
    selected_pf_id_medications.consultation_id.is_in(selected_pf_id_condition_ids)
).consultation_id.count_distinct_for_patient()

# count_pf_condition_and_med = selected_pf_id_conditions.where(
#     selected_pf_id_conditions.consultation_id.is_in(selected_pf_id_medication_ids)
# ).consultation_id.count_distinct_for_patient()


# Define defaults for measures
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
    numerator=count_pf_med_only,
)

measures.define_measure(
    name="pfcondition_with_pfid",
    numerator=count_pf_condition_only,
)

measures.define_measure(
    name="pfmed_and_pfcondition_with_pfid",
    numerator=count_pf_both,
)

measures.define_measure(
    name="pfconsultations_with_pfid_count",
    numerator=pf_consultation_count,
)

measures.define_measure(
    name="non_pfevents_with_pfid_count",
    numerator=nonpf_event_count,
)

measures.define_measure(
    name="non_pfmed_with_pfid_count",
    numerator=nonpf_med_count,
)
