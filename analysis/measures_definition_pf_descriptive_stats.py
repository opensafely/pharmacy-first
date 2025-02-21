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
measures.configure_disclosure_control(enabled=False)

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

# Select Pharmacy First conditions by ID and date
selected_pf_id_conditions = selected_events.where(
    selected_events.consultation_id.is_in(pf_ids)
).where(selected_events.snomedct_code.is_in(pf_conditions_codelist))

non_pf_condition_events = selected_events.except_where(
    selected_events.snomedct_code.is_in(
        pf_conditions_codelist
    )).except_where(selected_events.snomedct_code.is_in(pf_consultation_events_dict["pf_consultation_services_combined"])
)

has_pf_id_condition = selected_pf_id_conditions.exists_for_patient()
# Counts occurences of all Pharmacy First conditions per month
pf_condition_count = selected_pf_id_conditions.count_for_patient()
# Counts occurences of all non-Pharmacy First conditions from PF consultations per month
nonpf_condition_count = non_pf_condition_events.where(non_pf_condition_events.consultation_id.is_in(pf_ids)).count_for_patient()

# Select Pharmacy First Medications by ID and date
selected_pf_id_medications = selected_medications.where(
    selected_medications.consultation_id.is_in(pf_ids)
).where(selected_medications.dmd_code.is_in(pf_med_codelist))

selected_nonpf_id_medications = selected_medications.where(
    selected_medications.consultation_id.is_in(pf_ids)
).except_where(selected_medications.dmd_code.is_in(pf_med_codelist))


has_pf_id_medication = selected_pf_id_medications.exists_for_patient()
pf_med_count = selected_pf_id_medications.count_for_patient()
nonpf_med_count = selected_nonpf_id_medications.count_for_patient()

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

measures.define_measure(
    name="pfconsultations_month_count",
    numerator=pf_consultation_count,
)

measures.define_measure(
    name="pfconditions_month_count",
    numerator=pf_condition_count,
)

measures.define_measure(
    name="non_pfconditions_month_count",
    numerator=nonpf_condition_count,
)

measures.define_measure(
    name="pfmed_month_count",
    numerator=pf_med_count,
)

measures.define_measure(
    name="non_pfmed_month_count",
    numerator = nonpf_med_count,
)