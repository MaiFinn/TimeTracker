from datetime import date, timedelta

from timetracker.summary import (
    calculate_actual_hours,
    calculate_expected_hours,
    calculate_monthly_balance,
    calculate_monthly_expected_hours,
    calculate_work_balance,
    filter_work_entries_by_month,
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


def test_filter_work_entries_by_month():
    entries = [
        {"date": "2026-01-10"},
        {"date": "2026-01-20"},
        {"date": "2026-02-01"},
    ]

    filtered = filter_work_entries_by_month(
        entries,
        year=2026,
        month=1,
    )

    assert len(filtered) == 2


def test_calculate_monthly_expected_hours_respects_contract_start():
    contract = {
        "start_date": "2026-01-15",
        "hours_per_week": 7,
    }

    expected_hours = calculate_monthly_expected_hours(
        contract,
        year=2026,
        month=1,
    )

    assert expected_hours == 17.0


def test_calculate_monthly_expected_hours_before_contract_start():
    contract = {
        "start_date": "2026-03-01",
        "hours_per_week": 7,
    }

    expected_hours = calculate_monthly_expected_hours(
        contract,
        year=2026,
        month=2,
    )

    assert expected_hours == 0.0


def test_calculate_monthly_balance():
    contract = {
        "start_date": "2026-01-01",
        "hours_per_week": 7,
    }

    work_entries = [
        {
            "date": "2026-01-01",
            "total_time": "2:00:00",
        },
        {
            "date": "2026-01-02",
            "total_time": "1:00:00",
        },
        {
            "date": "2026-02-01",
            "total_time": "10:00:00",
        },
    ]

    balance = calculate_monthly_balance(
        contract,
        work_entries,
        year=2026,
        month=1,
    )

    assert balance["actual_hours"] == 3.0
    assert balance["expected_hours"] == 31.0
    assert balance["balance_hours"] == -28.0