from datetime import date
from analysis.dataset_definition_table1 import dataset

# Run the following command in the terminal to test the dataset definition dataset_definition_med_status_data_development
# opensafely exec ehrql:v1 assure analysis/test_pf_dataset_definition.py
# Index date = "2024-10-10"
test_data = {
    # Expected in population (test for age exclusions)
    # Female patient, 16 year old
    1: {
        "patients": {"date_of_birth": date(2008, 1, 1), "sex": "female"},
        "clinical_events": [
            {},
        ],
        "addresses": {},
        "ethnicity_from_sus": {},
        "practice_registrations": [{"start_date": date(2024, 3, 1)}],
        "expected_in_population": True,
        "expected_columns": {
            "uti_denominator": True,
            "shingles_denominator": False,
            "impetigo_denominator": True,
            "insectbite_denominator": True,
            "sorethroat_denominator": True,
            "sinusitis_denominator": True,
            "otitismedia_denominator": True,
            "pregnancy_status": False,
        },
    },
    # Expected in population (test for pregnancy exclusions)
    # Female patient, PREGNANT 15 year old
    2: {
        "patients": {"date_of_birth": date(2009, 1, 1), "sex": "female"},
        "clinical_events": [
            {
                # Pregnancy code
                "date": date(2024, 10, 3),
                "snomedct_code": "77386006",
            },
        ],
        "addresses": {},
        "ethnicity_from_sus": {},
        "practice_registrations": [{"start_date": date(2024, 3, 1)}],
        "expected_in_population": True,
        "expected_columns": {
            "uti_denominator": False,
            "shingles_denominator": False,
            "impetigo_denominator": False,
            "insectbite_denominator": False,
            "sorethroat_denominator": False,
            "sinusitis_denominator": False,
            "otitismedia_denominator": False,
            "pregnancy_status": True,
        },
    },
    # Expected in population (test for multiple diagnoses exclusions)
    # Female patient, 24 year old
    3: {
        "patients": {"date_of_birth": date(2000, 1, 1), "sex": "female"},
        "clinical_events": [
            {
                # 1st UTI diagnosis
                "date": date(2024, 10, 7),
                "snomedct_code": "1090711000000102",
            },
            {
                # 2nd UTI diagnosis
                "date": date(2024, 10, 8),
                "snomedct_code": "1090711000000102",
            },
            {
                # 3rd UTI diagnosis
                "date": date(2024, 10, 9),
                "snomedct_code": "1090711000000102",
            },
        ],
        "addresses": {},
        "ethnicity_from_sus": {},
        "practice_registrations": [{"start_date": date(2024, 3, 1)}],
        "expected_in_population": True,
        "expected_columns": {
            "uti_denominator": False,
            "shingles_denominator": True,
            "impetigo_denominator": True,
            "insectbite_denominator": True,
            "sorethroat_denominator": True,
            "sinusitis_denominator": True,
            "otitismedia_denominator": False,
            "pregnancy_status": False,
        },
    },
}
