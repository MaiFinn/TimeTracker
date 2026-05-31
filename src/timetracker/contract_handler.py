from dataclasses import asdict, dataclass
from pathlib import Path

from timetracker.config.paths import CONTRACT_FILE
from timetracker.storage.json_storage import save_json


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
    file_path: Path | None = None,
) -> None:
    """Create a new contract file."""

    if file_path is None:
        file_path = CONTRACT_FILE

    contract_details = Contract(
        company_name=company_name,
        start_date=start_date,
        salary_per_hour=salary_per_hour,
        hours_per_week=hours_per_week,
    )

    save_json(file_path, asdict(contract_details))