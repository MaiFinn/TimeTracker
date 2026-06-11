from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import logging

from timetracker.config.paths import WORK_ENTRIES_FILE
from timetracker.storage.json_storage import load_json, save_json
from timetracker.utils.time_utils import calculate_total_time

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
    file_path: Path | None = None,
) -> None:
    """Create a work entry."""

    if file_path is None:
        file_path = WORK_ENTRIES_FILE

    if entry_status not in VALID_ENTRY_STATUSES:
        raise ValueError(f"Invalid entry status: {entry_status}")

    logger.info(f"Writing work entry file to {file_path}.")

    parsed_start_time = datetime.strptime(start_time, "%H:%M").time()
    parsed_end_time = datetime.strptime(end_time, "%H:%M").time()

    duration = calculate_total_time(parsed_start_time, parsed_end_time)

    work_entry = WorkEntry(
        date=working_date,
        start_time=str(parsed_start_time),
        end_time=str(parsed_end_time),
        total_time=duration,
        entry_status=entry_status,
        note=note,
        attachments=attachments or [],
    )

    work_entries = load_json(file_path, default=[])
    work_entries.append(asdict(work_entry))

    save_json(file_path, work_entries)