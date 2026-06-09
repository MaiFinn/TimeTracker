import csv
from calendar import month_name
from datetime import date, datetime
from pathlib import Path

from timetracker.summary import (
    calculate_actual_hours,
    calculate_monthly_expected_hours,
    filter_work_entries_by_month,
)


def calculate_hours_by_status(work_entries: list[dict]) -> dict[str, float]:
    """Calculate hours grouped by entry status."""

    return {
        "worked": calculate_actual_hours(work_entries, ["worked"]),
        "cancelled_by_employer": calculate_actual_hours(
            work_entries,
            ["cancelled_by_employer"],
        ),
        "cancelled_by_employee": calculate_actual_hours(
            work_entries,
            ["cancelled_by_employee"],
        ),
    }


def get_month_range(work_entries: list[dict]) -> list[tuple[int, int]]:
    """Return sorted year-month pairs from work entries."""

    months = set()

    for entry in work_entries:
        entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
        months.add((entry_date.year, entry_date.month))

    return sorted(months)


def build_monthly_report_rows(
    contract: dict,
    work_entries: list[dict],
) -> list[dict]:
    """Build monthly report rows."""

    rows = []

    for year, month in get_month_range(work_entries):
        monthly_entries = filter_work_entries_by_month(
            work_entries,
            year,
            month,
        )

        hours_by_status = calculate_hours_by_status(monthly_entries)
        expected_hours = calculate_monthly_expected_hours(contract, year, month)

        balance = (
            hours_by_status["worked"]
            + hours_by_status["cancelled_by_employer"]
            - expected_hours
        )

        rows.append(
            {
                "period": f"{month_name[month]} {year}",
                "worked_hours": _round_hours(hours_by_status["worked"]),
                "employer_cancelled_hours": _round_hours(
                    hours_by_status["cancelled_by_employer"]
                ),
                "employee_cancelled_hours": _round_hours(
                    hours_by_status["cancelled_by_employee"]
                ),
                "expected_hours": _round_hours(expected_hours),
                "balance_hours": _round_hours(balance),
            }
        )

    return rows


def build_total_report_row(
    contract: dict,
    work_entries: list[dict],
) -> dict:
    """Build total report row."""

    hours_by_status = calculate_hours_by_status(work_entries)

    start_date = datetime.strptime(contract["start_date"], "%Y-%m-%d").date()
    today = date.today()

    days_since_start = max((today - start_date).days, 0)
    expected_hours = days_since_start / 7 * float(contract["hours_per_week"])

    balance = (
        hours_by_status["worked"]
        + hours_by_status["cancelled_by_employer"]
        - expected_hours
    )

    start_date = datetime.strptime(
        contract["start_date"],
        "%Y-%m-%d",
    ).date()

    today = date.today()

    period_label = (
        f"{start_date.strftime('%d.%m.%Y')} - "
        f"{today.strftime('%d.%m.%Y')}"
    )

    return {
        "period": period_label,
        "worked_hours": _round_hours(hours_by_status["worked"]),
        "employer_cancelled_hours": _round_hours(
            hours_by_status["cancelled_by_employer"]
        ),
        "employee_cancelled_hours": _round_hours(
            hours_by_status["cancelled_by_employee"]
        ),
        "expected_hours": _round_hours(expected_hours),
        "balance_hours": _round_hours(balance),
    }


def export_monthly_report_csv(
    contract: dict,
    work_entries: list[dict],
    file_path: Path,
) -> None:
    """Export monthly and total report as CSV."""

    rows = build_monthly_report_rows(contract, work_entries)
    rows.append(build_total_report_row(contract, work_entries))

    file_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "period",
        "worked_hours",
        "employer_cancelled_hours",
        "employee_cancelled_hours",
        "expected_hours",
        "balance_hours",
    ]

    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def _round_hours(value: float) -> float:
    """Round hour values to two decimal places."""

    return round(value, 2)