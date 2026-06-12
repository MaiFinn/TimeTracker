import logging

import typer

from timetracker.config.paths import DATABASE_FILE, LOG_FILE
from timetracker.contract_handler import create_contract
from timetracker.storage.sqlite_storage import load_contract, load_work_entries
from timetracker.summary import calculate_work_balance
from timetracker.utils.logger import setup_logger
from timetracker.work_entry_handler import create_work_entry


setup_logger(name="timetracker", log_file=LOG_FILE)
logger = logging.getLogger(__name__)

CURRENT_USER_ID = "finn"

app = typer.Typer(
    help="TimeTracker command-line interface.",
)


@app.command()
def summary() -> None:
    """Show working time summary."""

    contract = load_contract(DATABASE_FILE, CURRENT_USER_ID)
    work_entries = load_work_entries(DATABASE_FILE, CURRENT_USER_ID)

    if contract is None:
        typer.echo("No contract found. Please create a contract first.")
        return

    balance = calculate_work_balance(contract, work_entries)

    typer.echo(f"Actual hours: {balance['actual_hours']:.2f} h")
    typer.echo(f"Expected hours: {balance['expected_hours']:.2f} h")
    typer.echo(f"Balance: {balance['balance_hours']:.2f} h")


@app.command()
def create_new_contract(
    company_name: str = typer.Option(
        ...,
        "--company-name",
        "-c",
        help="Define company name, e.g. Audi.",
    ),
    start_date: str = typer.Option(
        ...,
        "--start-date",
        "-s",
        help="Start date of contract in YYYY-MM-DD format.",
    ),
    salary_per_hour: float = typer.Option(
        20.00,
        "--salary-per-hour",
        "-sph",
        help="Salary per hour.",
    ),
    hours_per_week: float = typer.Option(
        5.00,
        "--hours-per-week",
        "-hpw",
        help="Working hours per week.",
    ),
) -> None:
    """Create a new contract via CLI."""

    logger.info("Creating new contract via CLI.")

    create_contract(
        company_name=company_name,
        start_date=start_date,
        salary_per_hour=salary_per_hour,
        hours_per_week=hours_per_week,
        user_id=CURRENT_USER_ID,
    )

    logger.info("Contract successfully created.")
    typer.echo("Contract successfully created.")


@app.command()
def add_work_entry(
    date: str = typer.Option(..., "--working-date", "-wd"),
    start_time: str = typer.Option(..., "--start-time", "-st"),
    end_time: str = typer.Option(..., "--end-time", "-et"),
) -> None:
    """Create a new work entry."""

    logger.info("Create new work entry.")

    create_work_entry(
        working_date=date,
        start_time=start_time,
        end_time=end_time,
        user_id=CURRENT_USER_ID,
    )

    logger.info("Created new work entry.")
    typer.echo("Work entry successfully created.")


if __name__ == "__main__":
    app()