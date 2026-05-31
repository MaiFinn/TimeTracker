from datetime import date, timedelta

from timetracker.summary import (
    calculate_actual_hours,
    calculate_expected_hours,
    calculate_work_balance,
    parse_duration,
)


def test_parse_duration():
    duration = parse_duration("7:30:00")

    assert duration == timedelta(hours=7, minutes=30)


def test_calculate_actual_hours():
    work_entries = [
        {"total_time": "2:00:00"},
        {"total_time": "1:30:00"},
    ]

    actual_hours = calculate_actual_hours(work_entries)

    assert actual_hours == 3.5


def test_calculate_expected_hours():
    contract = {
        "start_date": "2026-01-01",
        "hours_per_week": 7,
    }

    today = date(2026, 1, 8)

    expected_hours = calculate_expected_hours(contract, today)

    assert expected_hours == 7.0


def test_calculate_work_balance():
    contract = {
        "start_date": "2026-01-01",
        "hours_per_week": 7,
    }

    work_entries = [
        {"total_time": "4:00:00"},
        {"total_time": "2:00:00"},
    ]

    today = date(2026, 1, 8)

    balance = calculate_work_balance(contract, work_entries, today)

    assert balance == {
        "actual_hours": 6.0,
        "expected_hours": 7.0,
        "balance_hours": -1.0,
    }