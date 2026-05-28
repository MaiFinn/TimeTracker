from datetime import datetime, date, time
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class workentry:
    "Container class for work entries."

    date: str
    start_time: time
    end_time: time
    total_time: float


def create_work_entry(
        working_date: str,
        start_time: str,
        end_time: str     
) -> json:
        
        """
        Create a work entry.

        Args:
            working_date (str): Date of working task
            start_time (str): Start of working
            end_time (str): End of working
        """
        
        parsed_start_time = datetime.strptime(start_time, "%H:%M").time()
        parsed_end_time = datetime.strptime(end_time, "%H:%M").time()

        start_datetime = datetime.combine(date.today(), parsed_start_time)
        end_datetime = datetime.combine(date.today(), parsed_end_time)

        duration = end_datetime - start_datetime

        work_entry = workentry(
                date=working_date,
                start_time=str(parsed_start_time),
                end_time=str(parsed_end_time),
                total_time=str(duration)
                )
        
        work_entry_dict = asdict(work_entry)
        file_path = Path("work_entries.json")

        if file_path.exists():
                with open(file_path, "r") as f:
                        work_entries = json.load(f)
        else:
                work_entries = []

        work_entries.append(work_entry_dict)

        with open(file_path, "w") as f:
                json.dump(work_entries, f)