from ehrql import INTERVAL, create_measures, months, case, when
from ehrql.tables.tpp import (
    clinical_events,
    practice_registrations,
    patients,
    addresses,
    ethnicity_from_sus,
)
from codelists import (
    pf_conditions_codelist,
    ethnicity_group6_codelist,
)

from pf_dataset import get_latest_ethnicity
from codelists import pf_consultation_events_dict
from config import (
    start_date_measure_pf_breakdown,
    monthly_intervals_measure_pf_breakdown,
)
from pf_variables_library import select_events

measures = create_measures()
measures.configure_dummy_data(population_size=1000)

start_date = start_date_measure_pf_breakdown
monthly_intervals = monthly_intervals_measure_pf_breakdown

registration = practice_registrations.for_patient_on(INTERVAL.end_date)
ethnicity_combined = get_latest_ethnicity(
    index_date=INTERVAL.start_date,
    clinical_events=clinical_events,
    ethnicity_codelist=ethnicity_group6_codelist,
    ethnicity_from_sus=ethnicity_from_sus,
)
# Age bands for age breakdown
age = patients.age_on(INTERVAL.start_date)
age_band = case(
    when((age >= 0) & (age < 20)).then("0-19"),
    when((age >= 20) & (age < 40)).then("20-39"),
    when((age >= 40) & (age < 60)).then("40-59"),
    when((age >= 60) & (age < 80)).then("60-79"),
    when(age >= 80).then("80+"),
    when(age.is_null()).then("Missing"),
)

# IMD groupings for IMD breakdown
imd = addresses.for_patient_on(INTERVAL.start_date).imd_rounded
max_imd = 32844
imd_quintile = case(
    when((imd >= 0) & (imd < int(max_imd * 1 / 5))).then("1 (Most Deprived)"),
    when(imd < int(max_imd * 2 / 5)).then("2"),
    when(imd < int(max_imd * 3 / 5)).then("3"),
    when(imd < int(max_imd * 4 / 5)).then("4"),
    when(imd <= max_imd).then("5 (Least Deprived)"),
    otherwise="Missing",
)

latest_region = case(
    when(registration.practice_nuts1_region_name.is_not_null()).then(
        registration.practice_nuts1_region_name
    ),
    otherwise="Missing",
)

pharmacy_first_ids = select_events(
    clinical_events,
    codelist=pf_consultation_events_dict["pf_consultation_services_combined"],
).consultation_id

# # Select clinical events in interval date range
selected_events = select_events(
    clinical_events, start_date=INTERVAL.start_date, end_date=INTERVAL.end_date
).where(clinical_events.consultation_id.is_in(pharmacy_first_ids))

# Breakdown metrics to be produced as graphs
breakdown_metrics = {
    "age_band": age_band,
    "sex": patients.sex,
    "imd": imd_quintile,
    "region": latest_region,
    "ethnicity": ethnicity_combined,
}

pf_consultation_events = select_events(
    selected_events,
    codelist=pf_consultation_events_dict["pf_consultation_services_combined"],
)
has_pf_consultation = pf_consultation_events.exists_for_patient()

# Define the denominator as the number of patients registered
denominator = (
    registration.exists_for_patient()
    & patients.sex.is_in(["male", "female"])
    & has_pf_consultation
)

# Create measures for pharmacy first services
for pharmacy_first_event, codelist in pf_consultation_events_dict.items():
    condition_events = selected_events.where(
        selected_events.snomedct_code.is_in(codelist)
    )

    # Define the numerator as the count of events for the condition
    numerator = condition_events.count_for_patient()

    # Measures for overall clinical services graph
    measures.define_measure(
        name=f"count_{pharmacy_first_event}",
        numerator=numerator,
        denominator=denominator,
        intervals=months(monthly_intervals).starting_on(start_date),
    )

    # Nested loop for each breakdown measure in clinical services
    for breakdown, variable in breakdown_metrics.items():
        measures.define_measure(
            name=f"count_{pharmacy_first_event}_by_{breakdown}",
            numerator=numerator,
            denominator=denominator,
            group_by={breakdown: variable},
            intervals=months(monthly_intervals).starting_on(start_date),
        )

# Create dictionary for clinical condition denominators
pf_condition_denominators = {
    "uncomplicated_urinary_tract_infection": denominator,
    "herpes_zoster": denominator,
    "impetigo": denominator,
    "infected_insect_bite": denominator,
    "acute_pharyngitis": denominator,
    "acute_sinusitis": denominator,
    "acute_otitis_media": denominator,
}

# Create measures for pharmacy first conditions
pharmacy_first_conditions_codes = {}
for codes, term in pf_conditions_codelist.items():
    normalised_term = term.lower().replace(" ", "_")
    codes = [codes]
    pharmacy_first_conditions_codes[normalised_term] = codes

for condition_name, condition_code in pharmacy_first_conditions_codes.items():
    condition_events = selected_events.where(
        selected_events.snomedct_code.is_in(condition_code)
    )

    # Define the numerator as the count of events for the condition
    numerator = condition_events.count_for_patient()

    # Measures for overall clinical services graph
    measures.define_measure(
        name=f"count_{condition_name}",
        numerator=numerator,
        denominator=pf_condition_denominators[condition_name],
        intervals=months(monthly_intervals).starting_on(start_date),
    )

    # Nested loop for each breakdown measure in clinical conditions
    for breakdown, variable in breakdown_metrics.items():
        measures.define_measure(
            name=f"count_{condition_name}_by_{breakdown}",
            numerator=numerator,
            denominator=pf_condition_denominators[condition_name],
            group_by={breakdown: variable},
            intervals=months(monthly_intervals).starting_on(start_date),
        )
