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


# Function to get events linked to a specified codelist
def select_events_from_codelist(event_frame, codelist):
    selected_events = event_frame.where(event_frame.snomedct_code.is_in(codelist))

    return selected_events


# Function to get events with specific consultation IDs
def select_events_by_consultation_id(event_frame, consultation_ids):
    selected_events = event_frame.where(
        event_frame.consultation_id.is_in(consultation_ids)
    )
    return selected_events


# Function to get events within a time frame
def select_events_between(event_frame, start_date, end_date):
    selected_events = event_frame.where(
        event_frame.date.is_on_or_between(start_date, end_date)
    )
    return selected_events


def select_events(
    event_frame, codelist=None, consultation_ids=None, start_date=None, end_date=None
):
    """
    Wrapper function to select events based on codelist, consultation IDs, or a date range.
    Allows combining multiple selection criteria.
    """
    selected_events = event_frame

    if codelist is not None:
        selected_events = select_events_from_codelist(selected_events, codelist)
    if consultation_ids is not None:
        selected_events = select_events_by_consultation_id(
            selected_events, consultation_ids
        )
    if start_date is not None and end_date is not None:
        selected_events = select_events_between(selected_events, start_date, end_date)

    return selected_events
