from dataclasses import asdict, dataclass
from pathlib import Path

from timetracker.config.paths import DATABASE_FILE
from timetracker.storage.sqlite_storage import save_contract


@dataclass
class Contract:
    """Container class for contract infos."""

    company_name: str
    start_date: str
    salary_per_hour: float
    hours_per_week: float


def create_contract(
    company_name: str,
    start_date: str,
    salary_per_hour: float,
    hours_per_week: float,
    user_id: str = "finn",
    database_file=DATABASE_FILE,
) -> None:
    """Create a new contract file."""

    contract_details = Contract(
        company_name=company_name,
        start_date=start_date,
        salary_per_hour=salary_per_hour,
        hours_per_week=hours_per_week,
    )

    save_contract(
        database_file=database_file,
        user_id=user_id,
        contract=asdict(contract_details),
    )