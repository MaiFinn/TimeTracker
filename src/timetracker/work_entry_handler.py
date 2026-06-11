from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import logging

from timetracker.config.paths import WORK_ENTRIES_FILE
from timetracker.storage.json_storage import load_json, save_json
from timetracker.utils.time_utils import calculate_total_time

from timetracker.config.paths import DATABASE_FILE
from timetracker.storage.sqlite_storage import (
    add_attachment,
    create_work_entry as create_sqlite_work_entry,
)

logger = logging.getLogger(__name__)

VALID_ENTRY_STATUSES = {
    "worked",
    "cancelled_by_employee",
    "cancelled_by_employer",
}


@dataclass
class WorkEntry:
    """Container class for work entries."""

    date: str
    start_time: str
    end_time: str
    total_time: str
    entry_status: str
    note: str = ""
    attachments: list[dict] | None = None


def create_work_entry(
    working_date: str,
    start_time: str,
    end_time: str,
    entry_status: str = "worked",
    note: str = "",
    attachments: list[dict] | None = None,
    user_id: str = "finn",
    database_file: Path = DATABASE_FILE,
) -> int:
    """Create a work entry in SQLite and return its id."""

    if entry_status not in VALID_ENTRY_STATUSES:
        raise ValueError(f"Invalid entry status: {entry_status}")

    parsed_start_time = datetime.strptime(start_time, "%H:%M").time()
    parsed_end_time = datetime.strptime(end_time, "%H:%M").time()

    duration = calculate_total_time(parsed_start_time, parsed_end_time)

    work_entry_id = create_sqlite_work_entry(
        database_file=database_file,
        user_id=user_id,
        date=working_date,
        start_time=str(parsed_start_time),
        end_time=str(parsed_end_time),
        total_time=duration,
        entry_status=entry_status,
        note=note,
    )

    for attachment in attachments or []:
        add_attachment(
            database_file=database_file,
            work_entry_id=work_entry_id,
            file_name=attachment["file_name"],
            file_path=attachment["file_path"],
        )

    return work_entry_id