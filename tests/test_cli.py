from typer.testing import CliRunner

import timetracker.cli as cli
from timetracker.config.paths import DATABASE_FILE
from timetracker.storage.sqlite_storage import load_work_entries


runner = CliRunner()


def test_add_work_entry():

    result = runner.invoke(
        cli.app,
        [
            "add-work-entry",
            "-wd",
            "2026-05-01",
            "-st",
            "10:00",
            "-et",
            "12:00",
        ],
    )

    assert result.exit_code == 0
    assert "Work entry successfully created." in result.output

    entries = load_work_entries(
        DATABASE_FILE,
        "finn",
    )

    assert any(
        entry["date"] == "2026-05-01"
        for entry in entries
    )