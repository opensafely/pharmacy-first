# Function which formats the unformatted conditions codelist, and retrieves its codes
# Unused in descriptive_stats.py, but will be used in later tickets (streamline breakdown.py)
def get_pf_condition_codes(pharmacy_first_conditions_codelist):
    pharmacy_first_conditions_codes = {}
    for codes, term in pharmacy_first_conditions_codelist.items():
        normalised_term = term.lower().replace(" ", "_")
        codes = [codes]
        pharmacy_first_conditions_codes[normalised_term] = codes

    return pharmacy_first_conditions_codes
