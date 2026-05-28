from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from time_tracker import TimeTracker


class TimeTrackerTests(unittest.TestCase):
    def test_contract_and_summary(self):
        with TemporaryDirectory() as tmpdir:
            tracker = TimeTracker(Path(tmpdir) / "tracker.json")
            tracker.set_contract("2026-01-01", salary_per_hour=20.0, hours_per_week=40, hours_per_month=160)
            tracker.add_entry("2026-05-01", 8, "feature work")
            tracker.add_entry("2026-05-02", 4, "meeting")

            hours, earnings = tracker.summary("2026-05")

            self.assertEqual(hours, 12)
            self.assertEqual(earnings, 240)

    def test_month_entries_only_returns_matching_month(self):
        with TemporaryDirectory() as tmpdir:
            tracker = TimeTracker(Path(tmpdir) / "tracker.json")
            tracker.add_entry("2026-05-10", 7.5, "dev")
            tracker.add_entry("2026-06-01", 8, "ops")

            may_entries = tracker.month_entries("2026-05")

            self.assertEqual(len(may_entries), 1)
            self.assertEqual(may_entries[0].day, "2026-05-10")
            self.assertEqual(may_entries[0].note, "dev")


if __name__ == "__main__":
    unittest.main()
