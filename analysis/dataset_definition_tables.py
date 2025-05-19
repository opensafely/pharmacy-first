from ehrql import create_dataset
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    practice_registrations,
    addresses,
    ethnicity_from_sus,
)
from config import start_date_dataset_tables, index_date_dataset_tables
from pf_dataset import (
    has_event,
    get_latest_ethnicity,
    get_age_band,
    get_imd,
)
from pf_variables_library import select_events
import codelists

launch_date = start_date_dataset_tables
index_date = index_date_dataset_tables

dataset = create_dataset()
dataset.configure_dummy_data(population_size=1000)


registration = practice_registrations.for_patient_on(index_date)
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(launch_date, index_date)
)

pf_consultation_events = select_events(
    selected_events,
    codelist=codelists.pf_consultation_events_dict["pf_consultation_services_combined"],
)

dataset.has_pf_consultation = pf_consultation_events.exists_for_patient()

pf_ids = pf_consultation_events.consultation_id
selected_pf_id_events = selected_events.where(
    selected_events.consultation_id.is_in(pf_ids)
)

# Columns for demographics table
dataset.sex = patients.sex
dataset.age = patients.age_on(index_date)
dataset.age_band = get_age_band(patients, index_date)
dataset.region = registration.practice_nuts1_region_name
dataset.imd = get_imd(addresses, index_date)
dataset.ethnicity = get_latest_ethnicity(
    index_date,
    clinical_events,
    codelists.ethnicity_group16_codelist,
    ethnicity_from_sus,
    grouping=16,
)

dataset.uti_numerator = has_event(
    selected_pf_id_events,
    codelists.uti_code,
)
dataset.sinusitis_numerator = has_event(
    selected_pf_id_events,
    codelists.sinusitis_code,
)
dataset.insectbite_numerator = has_event(
    selected_pf_id_events,
    codelists.insectbite_code,
)
dataset.otitismedia_numerator = has_event(
    selected_pf_id_events,
    codelists.otitismedia_code,
)
dataset.sorethroat_numerator = has_event(
    selected_pf_id_events,
    codelists.sorethroat_code,
)
dataset.shingles_numerator = has_event(
    selected_pf_id_events,
    codelists.shingles_code,
)
dataset.impetigo_numerator = has_event(
    selected_pf_id_events,
    codelists.impetigo_code,
)

dataset.define_population(
    registration.exists_for_patient()
    & patients.sex.is_in(["male", "female"])
)
