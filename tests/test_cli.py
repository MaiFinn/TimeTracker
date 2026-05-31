# tests/test_cli.py

from typer.testing import CliRunner
from timetracker.cli import app
import timetracker.cli as cli

runner = CliRunner()


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