import json
from pathlib import Path


def load_json(file_path: Path, default):
    """Load JSON data from a file.

    Args:
        file_path: Path to the JSON file.
        default: Default value returned if the file does not exist.

    Returns:
        Loaded JSON data or the default value.
    """
    if file_path.exists():
        with open(file_path, "r") as f:
            return json.load(f)

    return default


def save_json(file_path: Path, data) -> None:
    """Save data as JSON file.

    Args:
        file_path: Path to the JSON file.
        data: Data to save.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)