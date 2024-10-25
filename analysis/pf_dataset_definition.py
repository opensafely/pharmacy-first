from ehrql import INTERVAL, Measures, months, create_dataset
from ehrql.tables.tpp import patients, clinical_events, practice_registrations, ethnicity_from_sus

from pf_dataset import (
    get_uncomplicated_uti_denominator,
    get_shingles_denominator,
    get_impetigo_denominator,
    get_infected_insect_bites_denominator,
    get_acute_sore_throat_denominator,
    get_acute_sinusitis_denominator,
    get_acute_otitis_media_denominator,
    get_pf_clinical_events,
    get_pf_consultation_ids_from_events,
    get_latest_ethnicity,
    check_pregnancy_status_for_debug,
    pharmacy_first_event_codes
)

import codelists

index_date = "2024-10-10"
dataset = create_dataset()

pharmacy_first_ids = get_pf_consultation_ids_from_events(clinical_events, pharmacy_first_event_codes["combined_pf_service"])
selected_events = get_pf_clinical_events(pharmacy_first_ids)

registration = practice_registrations.for_patient_on(index_date)

# Create new columns for each denominator rule
dataset.uti_denominator = get_uncomplicated_uti_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.shingles_denominator = get_shingles_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.impetigo_denominator = get_impetigo_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.insect_bite_denominator = get_infected_insect_bites_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.sore_throat_denominator = get_acute_sore_throat_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.sinusitis_denominator = get_acute_sinusitis_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.otitis_media_denominator = get_acute_otitis_media_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.latest_ethnicity = get_latest_ethnicity(index_date, clinical_events, codelists.ethnicity_codelist, ethnicity_from_sus)
dataset.pregnancy_status_check = check_pregnancy_status_for_debug(index_date, selected_events, codelists.pregnancy_codelist)
dataset.define_population(registration.exists_for_patient() & patients.sex.is_in(["male", "female"]))