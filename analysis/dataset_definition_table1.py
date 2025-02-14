from ehrql import create_dataset
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    practice_registrations,
    addresses,
    ethnicity_from_sus,
)
from config import start_date_tables, index_date
from pf_variables_library import check_pregnancy_status
from pf_dataset import (
    get_uncomplicated_uti_denominator,
    get_shingles_denominator,
    get_impetigo_denominator,
    get_infected_insect_bites_denominator,
    get_acute_sore_throat_denominator,
    get_acute_sinusitis_denominator,
    get_acute_otitis_media_denominator,
    get_numerator,
    get_latest_ethnicity,
    get_age_band,
    get_imd,
)
from pf_variables_library import select_events
import codelists

launch_date = start_date_tables
index_date = index_date

dataset = create_dataset()
dataset.configure_dummy_data(population_size=10000)


registration = practice_registrations.for_patient_on(index_date)
selected_events = clinical_events.where(
    clinical_events.date.is_on_or_between(launch_date, index_date)
)

# Columns for demographics table
dataset.sex = patients.sex
dataset.age_band = get_age_band(patients, index_date)
dataset.region = registration.practice_nuts1_region_name
dataset.imd = get_imd(addresses, index_date)
dataset.ethnicity = get_latest_ethnicity(
    index_date,
    selected_events,
    codelists.ethnicity_group16_codelist,
    ethnicity_from_sus,
    grouping=16,
)


# Create new columns for each denominator rule for clinical conditions table
dataset.uti_denominator = get_uncomplicated_uti_denominator(
    index_date, patients, selected_events, codelists.pregnancy_codelist
)
dataset.shingles_denominator = get_shingles_denominator(
    index_date, patients, selected_events, codelists.pregnancy_codelist
)
dataset.impetigo_denominator = get_impetigo_denominator(
    index_date, patients, selected_events, codelists.pregnancy_codelist
)
dataset.insectbite_denominator = get_infected_insect_bites_denominator(
    index_date, patients, selected_events, codelists.pregnancy_codelist
)
dataset.sorethroat_denominator = get_acute_sore_throat_denominator(
    index_date, patients, selected_events, codelists.pregnancy_codelist
)
dataset.sinusitis_denominator = get_acute_sinusitis_denominator(
    index_date, patients, selected_events, codelists.pregnancy_codelist
)
dataset.otitismedia_denominator = get_acute_otitis_media_denominator(
    index_date, patients, selected_events, codelists.pregnancy_codelist
)
dataset.pregnancy_status = check_pregnancy_status(
    index_date, selected_events, codelists.pregnancy_codelist
)

dataset.uti_numerator = get_numerator(
    selected_events, codelists.uti_code, dataset.uti_denominator
)
dataset.sinusitis_numerator = get_numerator(
    selected_events, codelists.sinusitis_code, dataset.sinusitis_denominator
)
dataset.insectbite_numerator = get_numerator(
    selected_events, codelists.insectbite_code, dataset.insectbite_denominator
)
dataset.otitismedia_numerator = get_numerator(
    selected_events, codelists.otitismedia_code, dataset.otitismedia_denominator
)
dataset.sorethroat_numerator = get_numerator(
    selected_events, codelists.sorethroat_code, dataset.sorethroat_denominator
)
dataset.shingles_numerator = get_numerator(
    selected_events, codelists.shingles_code, dataset.shingles_denominator
)
dataset.impetigo_numerator = get_numerator(
    selected_events, codelists.impetigo_code, dataset.impetigo_denominator
)

pf_consultation_events = select_events(
    selected_events,
    codelist=codelists.pf_consultation_events_dict["pf_consultation_services_combined"],
)
has_pf_consultation = pf_consultation_events.exists_for_patient()

dataset.define_population(
    registration.exists_for_patient()
    & patients.sex.is_in(["male", "female"])
    & has_pf_consultation
)
