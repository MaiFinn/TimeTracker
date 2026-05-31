# src/timetracker/storage/json_storage.py

import json
from pathlib import Path


def load_json(file_path: Path, default):
    """Load JSON data from a file."""
    if file_path.exists():
        with open(file_path, "r") as f:
            return json.load(f)

    return default


def save_json(file_path: Path, data) -> None:
    """Save data as JSON file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)