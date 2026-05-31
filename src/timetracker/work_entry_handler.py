from dataclasses import asdict, dataclass
from datetime import date, datetime, time
from pathlib import Path
import logging

from timetracker.storage.json_storage import load_json, save_json

logger = logging.getLogger(__name__)


@dataclass
class WorkEntry:
    """Container class for work entries."""

    date: str
    start_time: str
    end_time: str
    total_time: str


def create_work_entry(
    working_date: str,
    start_time: str,
    end_time: str,
    file_path: Path | None = None,
) -> None:
    """Create a work entry."""

    if file_path is None:
        project_root = Path(__file__).resolve().parents[2]
        artifacts_dir = project_root / "artifacts"
        file_path = artifacts_dir / "work_entries.json"

    logger.info(f"Writing work entry file to {file_path}.")

    parsed_start_time = datetime.strptime(start_time, "%H:%M").time()
    parsed_end_time = datetime.strptime(end_time, "%H:%M").time()

    start_datetime = datetime.combine(date.today(), parsed_start_time)
    end_datetime = datetime.combine(date.today(), parsed_end_time)

    duration = end_datetime - start_datetime

    work_entry = WorkEntry(
        date=working_date,
        start_time=str(parsed_start_time),
        end_time=str(parsed_end_time),
        total_time=str(duration),
    )

    work_entries = load_json(file_path, default=[])
    work_entries.append(asdict(work_entry))

    save_json(file_path, work_entries)