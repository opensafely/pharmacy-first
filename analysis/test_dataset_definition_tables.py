from datetime import date
from analysis.dataset_definition_tables import dataset

# Run the following command in the terminal to test the dataset definition dataset_definition_med_status_data_development
# opensafely exec ehrql:v1 assure analysis/test_pf_dataset_definition.py
# Index date = "2024-10-10"
test_data = {
    # Expected in population (test for age exclusions)
    # Female patient, 16 year old
    1: {
        "patients": {
            "date_of_birth": date(2008, 1, 1),
            "sex": "female",
        },
        "clinical_events": [
            {},
        ],
        "addresses": {},
        "ethnicity_from_sus": {},
        "practice_registrations": [{"start_date": date(2024, 3, 1)}],
        "expected_in_population": True,
        "expected_columns": {
            "has_pf_consultation": False,
            "sex": "female",
            "age": 17,
        },
    },
}
