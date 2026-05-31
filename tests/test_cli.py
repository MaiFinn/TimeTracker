# tests/test_cli.py

from typer.testing import CliRunner
from timetracker.cli import app
import timetracker.cli as cli
from timetracker.storage.json_storage import save_json


runner = CliRunner()

def test_summary_with_contract(tmp_path, monkeypatch):
    contract_file = tmp_path / "contract.json"
    work_entries_file = tmp_path / "work_entries.json"

    save_json(
        contract_file,
        {
            "company_name": "Audi",
            "start_date": "2026-01-01",
            "salary_per_hour": 20.5,
            "hours_per_week": 7,
        },
    )

    save_json(
        work_entries_file,
        [
            {
                "date": "2026-01-02",
                "start_time": "10:00:00",
                "end_time": "12:00:00",
                "total_time": "2:00:00",
            }
        ],
    )

    monkeypatch.setattr(cli, "CONTRACT_FILE", contract_file)
    monkeypatch.setattr(cli, "WORK_ENTRIES_FILE", work_entries_file)

    result = runner.invoke(cli.app, ["summary"])

    assert result.exit_code == 0
    assert "Actual hours:" in result.output
    assert "Expected hours:" in result.output
    assert "Balance:" in result.output


def test_summary_without_contract(tmp_path, monkeypatch):

    contract_file = tmp_path / "contract.json"
    work_entries_file = tmp_path / "work_entries.json"

    monkeypatch.setattr(cli, "CONTRACT_FILE", contract_file)
    monkeypatch.setattr(cli, "WORK_ENTRIES_FILE", work_entries_file)
    result = runner.invoke(cli.app, ["summary"])

    assert result.exit_code == 0
    assert "No contract found" in result.output


def test_create_new_contract(tmp_path):
    file_path = tmp_path / "contract.json"

    result = runner.invoke(
        app,
        [
            "create-new-contract",
            "-c",
            "Audi",
            "-s",
            "2026-05-01",
            "-sph",
            "20.5",
            "-hpw",
            "2",
            "--file-path",
            str(file_path),
        ],
    )

    assert result.exit_code == 0
    assert "Contract successfully created." in result.output
    assert file_path.exists()

def test_add_work_entry(tmp_path):
    file_path = tmp_path / "work_entries.json"

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
            "--file-path",
            str(file_path),
        ],
    )

    assert result.exit_code == 0
    assert "Work entry successfully created." in result.output
    assert file_path.exists()