# Function which formats the unformatted conditions codelist, and retrieves its codes
def get_pf_condition_codes(pharmacy_first_conditions_codelist):
    pharmacy_first_conditions_codes = {}
    for codes, term in pharmacy_first_conditions_codelist.items():
        normalised_term = term.lower().replace(" ", "_")
        codes = [codes]
        pharmacy_first_conditions_codes[normalised_term] = codes

        pf_condition_codelist = [code for sublist in pharmacy_first_conditions_codes.values() for code in sublist]

    return pf_condition_codelist