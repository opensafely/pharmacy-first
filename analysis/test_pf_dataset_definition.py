from datetime import date
from analysis.pf_dataset_definition import dataset

# Run the following command in the terminal to test the dataset definition dataset_definition_med_status_data_development
# opensafely exec ehrql:v1 assure analysis/test_pf_dataset_definition.py
# Index date = "2024-10-10"
test_data = {
    # Expected in population (test for age exclusions)
    # Female patient, 1 year old
    1: {
        "patients": {"date_of_birth": date(2023,1,1),
                     "sex": "female"},
        "clinical_events": [
            {},
        ],
        "ethnicity_from_sus": {
            "code": "A"
        },
        "practice_registrations": [{"start_date": date(2024,3,1)}],

        "expected_in_population": True,
        "expected_columns": {
            "uti_denominator": False,
            "shingles_denominator": False,
            "impetigo_denominator": True,
            "insect_bite_denominator": True,
            "sore_throat_denominator": False,
            "sinusitis_denominator": False,
            "otitis_media_denominator": True,
            "latest_ethnicity": "White",
            "pregnancy_status_check": False,

        },
    },
    # Expected in population (test for pregnancy exclusions)
    # Female patient, 24 years old and PREGNANT
    2:{
        "patients": {"date_of_birth": date(2000, 1, 1),
                     "sex": "female"},
        "clinical_events": [
            {
                # otitis media code
                "date": date(2024, 10, 1),
                "snomedct_code": "3110003",
            },
            {
                # Pregnancy code
                "date": date(2024, 10, 3),
                "snomedct_code": "77386006"
            }
        ],
        "ethnicity_from_sus": {
            "code": "J"
        },
        "practice_registrations": [{"start_date": date(2020,3,1)}],
  
        "expected_in_population": True,
        "expected_columns": {
            "uti_denominator": False,
            "shingles_denominator": False,
            "impetigo_denominator": True,
            "insect_bite_denominator": True,
            "sore_throat_denominator": True,
            "sinusitis_denominator": True,
            "otitis_media_denominator": False,
            "latest_ethnicity": "Asian or Asian British",
            "pregnancy_status_check": True,

        },
    },

    # Expected in population (test for multiple diagnosis exclusion -impetigo)
    # Male, 24 years old, TWO impetigo diagnoses
    3:{
        "patients": {"date_of_birth": date(2000, 1, 1),
                     "sex": "male"},
        "clinical_events": [
            {
                # 1st impetigo diagnosis
                "date": date(2024, 10, 9),
                "snomedct_code": "48277006",
            },
            {
                # 2nd impetigo diagnosis
                "date": date(2024, 10, 10),
                "snomedct_code": "48277006"
            }
        ],
        "ethnicity_from_sus": {
            "code": "J"
        },
        "practice_registrations": [{"start_date": date(2020,3,1)}],
  
        "expected_in_population": True,
        "expected_columns": {
            "uti_denominator": False,
            "shingles_denominator": True,
            "impetigo_denominator": False,
            "insect_bite_denominator": True,
            "sore_throat_denominator": True,
            "sinusitis_denominator": True,
            "otitis_media_denominator": False,
            "latest_ethnicity": "Asian or Asian British",
            "pregnancy_status_check": False,

        },
    },
}