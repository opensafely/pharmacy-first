from ehrql import create_dataset, case, when
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    practice_registrations,
    addresses,
    ethnicity_from_sus,
)
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
    get_imd
)

import codelists

index_date = "2024-12-31"
dataset = create_dataset()

registration = practice_registrations.for_patient_on(index_date)
selected_events = clinical_events.where(clinical_events.date.is_on_or_before(index_date))

# Columns for demographics table
dataset.sex = patients.sex
dataset.age_band = get_age_band(patients, index_date)
dataset.region = registration.practice_nuts1_region_name
dataset.imd = get_imd(addresses, index_date)
dataset.ethnicity = get_latest_ethnicity(
    index_date, selected_events, codelists.ethnicity_group16_codelist, ethnicity_from_sus, grouping=16
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
uti_code = ["1090711000000102"]
sinusitis_code = ["15805002"]
insectbite_code = ["262550002"]
otitismedia_code = ["3110003"]
sorethroat_code = ["363746003"]
shingles_code = ["4740000"]
impetigo_code = ["48277006"]

dataset.uti_numerator = get_numerator(selected_events, uti_code, dataset.uti_denominator)
dataset.sinusitis_numerator = get_numerator(selected_events, sinusitis_code, dataset.sinusitis_denominator)
dataset.insectbite_numerator = get_numerator(selected_events, insectbite_code, dataset.insectbite_denominator)
dataset.otitismedia_numerator = get_numerator(selected_events, otitismedia_code, dataset.otitismedia_denominator)
dataset.sorethroat_numerator = get_numerator(selected_events, sorethroat_code, dataset.sorethroat_denominator)
dataset.shingles_numerator = get_numerator(selected_events, shingles_code, dataset.shingles_denominator)
dataset.impetigo_numerator = get_numerator(selected_events, impetigo_code, dataset.impetigo_denominator)

dataset.define_population(
    registration.exists_for_patient() & patients.sex.is_in(["male", "female"])
)
