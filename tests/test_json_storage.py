from timetracker.storage.json_storage import load_json, save_json


def test_load_json_returns_default_if_file_does_not_exist(tmp_path):
    file_path = tmp_path / "missing.json"

    data = load_json(file_path, default=[])

    assert data == []


def test_save_json_creates_json_file(tmp_path):
    file_path = tmp_path / "data.json"
    data = {"name": "TimeTracker", "version": 1}

    save_json(file_path, data)

    assert file_path.exists()


def test_load_json_reads_saved_data(tmp_path):
    file_path = tmp_path / "data.json"
    expected_data = {
        "entries": [
            {
                "date": "2026-05-30",
                "total_time": "2:00:00",
            }
        ]
    }

    save_json(file_path, expected_data)
    loaded_data = load_json(file_path, default={})

    assert loaded_data == expected_data


def test_save_json_creates_parent_directories(tmp_path):
    file_path = tmp_path / "nested" / "folder" / "data.json"
    data = {"status": "ok"}

    save_json(file_path, data)

    assert file_path.exists()
    assert load_json(file_path, default={}) == data