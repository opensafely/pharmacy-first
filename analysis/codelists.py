from ehrql import codelist_from_csv

# Import pharmacy first conditions codelist
pharmacy_first_conditions_codelist = codelist_from_csv(
    "codelists/user-chriswood-pharmacy-first-clinical-pathway-conditions.csv",
    column="code",
    category_column="term",
)

# Import ethnicity codelist
ethnicity_codelist = codelist_from_csv(
    "codelists/opensafely-ethnicity-snomed-0removed.csv",
    column="snomedcode",
    category_column="Grouping_6",
)

# Import pregnancy codelist
pregnancy_codelist = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-preg_cod.csv",
    column="code",
    category_column="term",
)

acute_otitis_media_tx_cod = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-acute-otitis-media-treatment-dmd.csv",
    column="code",
)

impetigo_treatment_tx_cod = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-impetigo-treatment-dmd.csv",
    column="code",
)

infected_insect_bites_tx_cod = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-infected-insect-bites-treatment-dmd.csv",
    column="code",
)

shingles_treatment_tx_cod = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-shingles-treatment-dmd.csv",
    column="code",
)

sinusitis_tx_cod = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-sinusitis-treatment-dmd.csv",
    column="code",
)

sore_throat_tx_cod = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-sore-throat-treatment-dmd.csv",
    column="code",
)

urinary_tract_infection_tx_cod = codelist_from_csv(
    "codelists/opensafely-pharmacy-first-urinary-tract-infection-treatment-dmd.csv",
    column="code",
)

pharmacy_first_med_codelist = (
    acute_otitis_media_tx_cod
    + impetigo_treatment_tx_cod
    + infected_insect_bites_tx_cod
    + shingles_treatment_tx_cod
    + sinusitis_tx_cod
    + sore_throat_tx_cod
    + urinary_tract_infection_tx_cod
)
# Community Pharmacist Consultation Service for minor illness - 1577041000000109
# Pharmacy First service - 983341000000102
pharmacy_first_consultation_codelist = ["1577041000000109", "983341000000102"]

# PF codes separated for individual analysis
pharmacy_first_event_codes = {
    # Community Pharmacist (CP) Consultation Service for minor illness (procedure)
    "consultation_service": ["1577041000000109"],
    # Pharmacy First service (qualifier value)
    "pharmacy_first_service": ["983341000000102"],
    "combined_pf_service": ["1577041000000109", "983341000000102"],
}
