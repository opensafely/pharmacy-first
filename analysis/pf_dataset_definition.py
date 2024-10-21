from ehrql import INTERVAL, Measures, months, create_dataset
from ehrql.tables.tpp import patients, clinical_events, practice_registrations

from pf_dataset import (
    get_uncomplicated_uti_denominator,
    get_shingles_denominator,
    get_impetigo_denominator,
    get_infected_insect_bites_denominator,
    get_acute_sore_throat_denominator,
    get_acute_sinusitis_denominator,
    get_acute_otitis_media_denominator,
)

from measures_definition_pf_codes_conditions import ( 
    pharmacy_first_ids,
)

import codelists


index_date = "2024-01-01"
dataset = create_dataset()

selected_events = (clinical_events.where(
    clinical_events.date.is_on_or_before(index_date))
.where(clinical_events.consultation_id.is_in(pharmacy_first_ids))
)

registration = practice_registrations.for_patient_on(index_date)

dataset.uti = get_uncomplicated_uti_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.shingles = get_shingles_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.impetigo = get_impetigo_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.insect = get_infected_insect_bites_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.sore_throat = get_acute_sore_throat_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.sinusitis = get_acute_sinusitis_denominator(index_date, selected_events, codelists.pregnancy_codelist)
dataset.otitis_media = get_acute_otitis_media_denominator(index_date, selected_events, codelists.pregnancy_codelist)

dataset.define_population(patients.exists_for_patient() & registration.exists_for_patient() & patients.sex.is_in(["male", "female"]))