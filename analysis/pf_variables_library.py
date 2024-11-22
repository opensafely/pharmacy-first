# Function to check status of a condition within a specified time window
from ehrql import months


def check_pregnancy_status(index_date, selected_events, codelist):
    return (
        selected_events.where(selected_events.snomedct_code.is_in(codelist))
        .where(
            selected_events.date.is_on_or_between(index_date - months(1), index_date)
        )
        .exists_for_patient()
    )


# Function to count number of coded events within a specified time window
def count_past_events(index_date, selected_events, codelist, num_months):
    return (
        selected_events.where(selected_events.snomedct_code.is_in(codelist))
        .where(
            selected_events.date.is_on_or_between(
                index_date - months(num_months), index_date
            )
        )
        .count_for_patient()
    )

# Function to get consultation IDs linked to a specified codelist
def get_consultation_ids(clinical_events, codelist):
    consultation_ids = clinical_events.where(
    clinical_events.snomedct_code.is_in(
        codelist
    )
    ).consultation_id   

    return consultation_ids

# Function to get events with specific consultation IDs
def get_consultationid_events(event_frame, consultation_ids):
    selected_events = event_frame.where(
        event_frame.consultation_id.is_in(consultation_ids)
    )
    return selected_events