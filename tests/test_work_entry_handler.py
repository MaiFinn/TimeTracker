from timetracker.work_entry_handler import create_work_entry
import json
from datetime import datetime, date, time

def test_work_entry_handler(tmp_path):
    
    date = "2026-02-10"
    start_time = "10:00"
    end_time = "15:00"
    file_path = tmp_path / "work_entries.json"

    create_work_entry(
    working_date=date,
    start_time=start_time,
    end_time=end_time,
    entry_status="worked",
    file_path=file_path,
)

    with open(file_path, "r") as f:
        data = json.load(f)
    
    assert file_path.exists()
    
    entry = data[0]

    assert entry == {
        "date": "2026-02-10",
        "start_time": "10:00:00",
        "end_time": "15:00:00",
        "total_time": "5:00:00",
        "entry_status": "worked",
        "note": "",
        "attachments": [],
    }

    assert isinstance(entry["date"], str)
    assert isinstance(entry["start_time"], str)
    assert isinstance(entry["end_time"], str)
    assert isinstance(entry["total_time"], str)