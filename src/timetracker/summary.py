from calendar import monthrange
from datetime import date, datetime, timedelta


def parse_duration(duration: str) -> timedelta:
    """Parse duration string in H:MM:SS format."""
    hours, minutes, seconds = duration.split(":")

    return timedelta(
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds),
    )


def filter_work_entries_by_month(
    work_entries: list[dict],
    year: int,
    month: int,
) -> list[dict]:
    """Filter work entries by year and month."""
    filtered_entries = []

    for entry in work_entries:
        entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()

        if entry_date.year == year and entry_date.month == month:
            filtered_entries.append(entry)

    return filtered_entries


def calculate_actual_hours(work_entries: list[dict]) -> float:
    """Calculate actual worked hours."""
    total_duration = timedelta()

    for entry in work_entries:
        total_duration += parse_duration(entry["total_time"])

    return total_duration.total_seconds() / 3600


def calculate_expected_hours(
    contract: dict,
    today: date | None = None,
) -> float:
    """Calculate expected working hours."""
    if today is None:
        today = date.today()

    start_date = datetime.strptime(contract["start_date"], "%Y-%m-%d").date()
    days_since_start = max((today - start_date).days, 0)

    return days_since_start / 7 * float(contract["hours_per_week"])


def calculate_work_balance(
    contract: dict,
    work_entries: list[dict],
    today: date | None = None,
) -> dict:
    """Calculate work balance."""
    actual_hours = calculate_actual_hours(work_entries)
    expected_hours = calculate_expected_hours(contract, today)

    return {
        "actual_hours": actual_hours,
        "expected_hours": expected_hours,
        "balance_hours": actual_hours - expected_hours,
    }


def calculate_monthly_expected_hours(
    contract: dict,
    year: int,
    month: int,
) -> float:
    """Calculate expected working hours for a specific month.

    The contract start date is respected. If the selected month is before
    the contract start, expected hours are 0.
    """
    contract_start = datetime.strptime(contract["start_date"], "%Y-%m-%d").date()

    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])

    if month_end < contract_start:
        return 0.0

    effective_start = max(month_start, contract_start)
    days_in_period = (month_end - effective_start).days + 1

    return days_in_period / 7 * float(contract["hours_per_week"])


def calculate_monthly_balance(
    contract: dict,
    work_entries: list[dict],
    year: int,
    month: int,
) -> dict:
    """Calculate balance for a specific month."""
    filtered_entries = filter_work_entries_by_month(
        work_entries,
        year,
        month,
    )

    actual_hours = calculate_actual_hours(filtered_entries)
    expected_hours = calculate_monthly_expected_hours(contract, year, month)

    return {
        "actual_hours": actual_hours,
        "expected_hours": expected_hours,
        "balance_hours": actual_hours - expected_hours,
    }