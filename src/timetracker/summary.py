from datetime import date, datetime, timedelta


def parse_duration(duration: str) -> timedelta:
    """Parse duration string in H:MM:SS format."""

    hours, minutes, seconds = duration.split(":")

    return timedelta(
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds),
    )


def calculate_actual_hours(work_entries: list[dict]) -> float:
    """Calculate actual worked hours from work entries."""

    total_duration = timedelta()

    for entry in work_entries:
        total_duration += parse_duration(entry["total_time"])

    return total_duration.total_seconds() / 3600


def calculate_expected_hours(contract: dict, today: date | None = None) -> float:
    """Calculate expected working hours since contract start."""

    if today is None:
        today = date.today()

    start_date = datetime.strptime(contract["start_date"], "%Y-%m-%d").date()
    days_since_start = (today - start_date).days

    expected_hours = days_since_start / 7 * float(contract["hours_per_week"])

    return expected_hours


def calculate_work_balance(
    contract: dict,
    work_entries: list[dict],
    today: date | None = None,
) -> dict:
    """Calculate actual, expected and balance hours."""

    actual_hours = calculate_actual_hours(work_entries)
    expected_hours = calculate_expected_hours(contract, today)

    return {
        "actual_hours": actual_hours,
        "expected_hours": expected_hours,
        "balance_hours": actual_hours - expected_hours,
    }