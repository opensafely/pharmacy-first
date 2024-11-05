from ehrql import create_dataset
from ehrql.tables.tpp import (
    patients,
    clinical_events,
    practice_registrations,
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
)

import codelists

index_date = "2024-10-10"
dataset = create_dataset()

registration = practice_registrations.for_patient_on(index_date)

# Create new columns for each denominator rule
dataset.uti_denominator = get_uncomplicated_uti_denominator(
    index_date, patients, clinical_events, codelists.pregnancy_codelist
)

dataset.shingles_denominator = get_shingles_denominator(
    index_date, patients, clinical_events, codelists.pregnancy_codelist
)

dataset.impetigo_denominator = get_impetigo_denominator(
    index_date, patients, clinical_events, codelists.pregnancy_codelist
)

dataset.insectbite_denominator = get_infected_insect_bites_denominator(
    index_date, patients, clinical_events, codelists.pregnancy_codelist
)

dataset.sorethroat_denominator = get_acute_sore_throat_denominator(
    index_date, patients, clinical_events, codelists.pregnancy_codelist
)

dataset.sinusitis_denominator = get_acute_sinusitis_denominator(
    index_date, patients, clinical_events, codelists.pregnancy_codelist
)

dataset.otitismedia_denominator = get_acute_otitis_media_denominator(
    index_date, patients, clinical_events, codelists.pregnancy_codelist
)

dataset.pregnancy_status = check_pregnancy_status(
    index_date, clinical_events, codelists.pregnancy_codelist
)

dataset.define_population(
    registration.exists_for_patient() & patients.sex.is_in(["male", "female"])
)
