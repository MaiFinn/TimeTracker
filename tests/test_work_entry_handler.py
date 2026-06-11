from timetracker.database.schema import initialize_database
from timetracker.storage.sqlite_storage import load_work_entries
from timetracker.work_entry_handler import create_work_entry


def test_work_entry_handler(tmp_path):

    database_file = tmp_path / "test.db"

    initialize_database(database_file)

    create_work_entry(
        working_date="2026-02-10",
        start_time="10:00",
        end_time="15:00",
        entry_status="worked",
        database_file=database_file,
    )

    entries = load_work_entries(
        database_file,
        "finn",
    )

    assert len(entries) == 1

    entry = entries[0]

    assert entry["date"] == "2026-02-10"
    assert entry["start_time"] == "10:00:00"
    assert entry["end_time"] == "15:00:00"
    assert entry["total_time"] == "5:00:00"
    assert entry["entry_status"] == "worked"