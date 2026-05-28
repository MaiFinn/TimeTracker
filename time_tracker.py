from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional


@dataclass
class Contract:
    start_date: str
    salary_per_hour: float
    hours_per_week: float
    hours_per_month: float


@dataclass
class WorkEntry:
    day: str
    hours: float
    note: str = ""


@dataclass
class TrackerData:
    contract: Optional[Contract] = None
    entries: list[WorkEntry] = field(default_factory=list)


class TimeTracker:
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.data = self._load()

    def _load(self) -> TrackerData:
        if not self.data_file.exists():
            return TrackerData()
        raw = json.loads(self.data_file.read_text())
        contract = Contract(**raw["contract"]) if raw.get("contract") else None
        entries = [WorkEntry(**entry) for entry in raw.get("entries", [])]
        return TrackerData(contract=contract, entries=entries)

    def save(self) -> None:
        payload = {
            "contract": asdict(self.data.contract) if self.data.contract else None,
            "entries": [asdict(entry) for entry in self.data.entries],
        }
        self.data_file.write_text(json.dumps(payload, indent=2))

    def set_contract(
        self, start_date: str, salary_per_hour: float, hours_per_week: float, hours_per_month: float
    ) -> None:
        _parse_date(start_date)
        self.data.contract = Contract(
            start_date=start_date,
            salary_per_hour=salary_per_hour,
            hours_per_week=hours_per_week,
            hours_per_month=hours_per_month,
        )
        self.save()

    def add_entry(self, day: str, hours: float, note: str = "") -> None:
        _parse_date(day)
        if hours < 0:
            raise ValueError("hours must be non-negative")
        self.data.entries.append(WorkEntry(day=day, hours=hours, note=note))
        self.data.entries.sort(key=lambda item: item.day)
        self.save()

    def month_entries(self, month: str) -> list[WorkEntry]:
        _parse_month(month)
        return [entry for entry in self.data.entries if entry.day.startswith(month)]

    def summary(self, month: Optional[str] = None) -> tuple[float, Optional[float]]:
        entries = self.month_entries(month) if month else self.data.entries
        total_hours = sum(entry.hours for entry in entries)
        if not self.data.contract:
            return total_hours, None
        return total_hours, total_hours * self.data.contract.salary_per_hour


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_month(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track working hours with notes and contract details.")
    parser.add_argument("--file", default="tracker.json", help="Path to tracker JSON file.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Set contract details.")
    init_parser.add_argument("--start-date", required=True)
    init_parser.add_argument("--salary-per-hour", required=True, type=float)
    init_parser.add_argument("--hours-per-week", required=True, type=float)
    init_parser.add_argument("--hours-per-month", required=True, type=float)

    add_parser = subparsers.add_parser("add", help="Add worked hours for a day.")
    add_parser.add_argument("--date", required=True)
    add_parser.add_argument("--hours", required=True, type=float)
    add_parser.add_argument("--note", default="")

    summary_parser = subparsers.add_parser("summary", help="Show hours and earnings summary.")
    summary_parser.add_argument("--month", help="Filter by month, format YYYY-MM.")

    calendar_parser = subparsers.add_parser("calendar", help="Show calendar-style entry list.")
    calendar_parser.add_argument("--month", required=True, help="Month format YYYY-MM.")

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    tracker = TimeTracker(Path(args.file))

    if args.command == "init":
        tracker.set_contract(
            start_date=args.start_date,
            salary_per_hour=args.salary_per_hour,
            hours_per_week=args.hours_per_week,
            hours_per_month=args.hours_per_month,
        )
        print("Contract details saved.")
        return

    if args.command == "add":
        tracker.add_entry(day=args.date, hours=args.hours, note=args.note)
        print("Work entry added.")
        return

    if args.command == "summary":
        hours, earnings = tracker.summary(month=args.month)
        if args.month:
            print(f"Summary for {args.month}:")
        else:
            print("Summary:")
        print(f"Total hours: {hours:.2f}")
        if earnings is not None:
            print(f"Estimated earnings: {earnings:.2f}")
        return

    if args.command == "calendar":
        entries = tracker.month_entries(args.month)
        print(f"Calendar for {args.month}")
        if not entries:
            print("No entries recorded.")
            return
        for entry in entries:
            note_suffix = f" - {entry.note}" if entry.note else ""
            print(f"{entry.day}: {entry.hours:.2f}h{note_suffix}")


if __name__ == "__main__":
    main()
