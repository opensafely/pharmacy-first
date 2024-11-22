
def get_pf_condition_codes(pharmacy_first_conditions_codelist):
    pharmacy_first_conditions_codes = {}
    for codes, term in pharmacy_first_conditions_codelist.items():
        normalised_term = term.lower().replace(" ", "_")
        codes = [codes]
        pharmacy_first_conditions_codes[normalised_term] = codes

        pf_condition_codelist = [code for sublist in pharmacy_first_conditions_codes.values() for code in sublist]

    return pf_condition_codelist

def get_consultation_ids(clinical_events, codelist):
    pharmacy_first_ids = clinical_events.where(
    clinical_events.snomedct_code.is_in(
        codelist
    )
    ).consultation_id   

    return pharmacy_first_ids

def get_selected_events(table, codes, INTERVAL):
    selected_events = table.where(
        table.date.is_on_or_between(INTERVAL.start_date, INTERVAL.end_date)
    ).where(table.consultation_id.is_in(codes))

    return selected_events