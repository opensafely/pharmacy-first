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
