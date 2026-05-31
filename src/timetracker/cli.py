from pathlib import Path
import typer
import logging

from timetracker.utils.logger import setup_logger
from timetracker.work_entry_handler import create_work_entry
from timetracker.contract_handler import create_contract
from timetracker.storage.json_storage import load_json
from timetracker.summary import calculate_work_balance

setup_logger(name="timetracker", log_file="artifacts/logs/timetracker.log")
logger = logging.getLogger(__name__)

CONTRACT_FILE = Path("artifacts/contract.json")
WORK_ENTRIES_FILE = Path("artifacts/work_entries.json")

app = typer.Typer(
    help="TimeTracker command-line interface.",
)

@app.command()
def summary() -> None:
    """Show working time summary."""

    contract = load_json(CONTRACT_FILE, default=None)
    work_entries = load_json(WORK_ENTRIES_FILE, default=[])

    if contract is None:
        typer.echo("No contract found. Please create a contract first.")
        return

    balance = calculate_work_balance(contract, work_entries)

    typer.echo(f"Actual hours: {balance['actual_hours']:.2f} h")
    typer.echo(f"Expected hours: {balance['expected_hours']:.2f} h")
    typer.echo(f"Balance: {balance['balance_hours']:.2f} h")

@app.command()
def create_new_contract(
    company_name: str = typer.Option(..., "--company-name", "-c", help="Define company name, e.g. Audi."),
    start_date: str = typer.Option(..., "--start-date", "-s", help="Start date of contract in YYYY-MM-DD format."),
    salary_per_hour: float = typer.Option(20.00, "--salary-per-hour", "-sph", help="Salary per hour."),
    hours_per_week: float = typer.Option(5.00, "--hours-per-week", "-hpw", help="Working hours per week."),
    file_path: Path | None = typer.Option(None, help="Optional define specific file path for contract.json file."),
) -> None:
    """
    Create a new contract via CLI.

    Args:
        company_name (str, optional): Defaults to typer.Option(..., help="Define company name, e.g. Audi.").
        start_date (str, optional): Defaults to typer.Option(..., help="Start date of contract in YYYY-MM-DD format.").
        salary_per_hour (float, optional): Defaults to typer.Option(0.01, help="Salary per hour.").
        hours_per_week (float, optional): Defaults to typer.Option(0.01, help="Working hours per week.").
        file_path (Path, optional): Defaults to typer.Option(..., help="Optional define specific file path for contract.json file.").
    """

    logger.info("Creating new contract via CLI.")

    create_contract(
        company_name=company_name,
        start_date=start_date,
        salary_per_hour=salary_per_hour,
        hours_per_week=hours_per_week,
        file_path=file_path,
    )

    logger.info("Contract successfully created.")
    typer.echo("Contract successfully created.")

@app.command()
def add_work_entry(
    date: str = typer.Option(..., "--working-date", "-wd"),
    start_time: str = typer.Option(..., "--start-time", "-st"),
    end_time: str = typer.Option(..., "--end-time", "-et"),
    file_path: Path | None = typer.Option(None, "--file-path"),
) -> None:
    """Create a new work entry."""

    logger.info("Create new work entry.")

    create_work_entry(
        date,
        start_time,
        end_time,
        file_path=file_path,
    )

    logger.info("Created new work entry.")
    typer.echo("Work entry successfully created.")

if __name__ == "__main__":
    app()