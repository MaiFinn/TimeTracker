from timetracker.config.paths import CONTRACT_FILE, DATABASE_FILE, WORK_ENTRIES_FILE
from timetracker.database.schema import initialize_database
from timetracker.storage.json_storage import load_json
from timetracker.storage.sqlite_storage import (
    count_work_entries,
    create_work_entry,
    save_contract,
)


DEFAULT_USER_ID = "finn"


def migrate_contract() -> None:
    """Migrate contract from JSON to SQLite."""

    contract = load_json(CONTRACT_FILE, default=None)

    if contract is None:
        return

    save_contract(
        database_file=DATABASE_FILE,
        user_id=DEFAULT_USER_ID,
        contract=contract,
    )


def migrate_work_entries() -> None:
    """Migrate work entries from JSON to SQLite."""

    if count_work_entries(DATABASE_FILE, DEFAULT_USER_ID) > 0:
        return

    work_entries = load_json(WORK_ENTRIES_FILE, default=[])

    for entry in work_entries:
        create_work_entry(
            database_file=DATABASE_FILE,
            user_id=DEFAULT_USER_ID,
            date=entry["date"],
            start_time=entry["start_time"],
            end_time=entry["end_time"],
            total_time=entry["total_time"],
            entry_status=entry.get("entry_status", "worked"),
            note=entry.get("note", ""),
        )


def main() -> None:
    """Run JSON to SQLite migration."""

    initialize_database(DATABASE_FILE)
    migrate_contract()
    migrate_work_entries()


if __name__ == "__main__":
    main()