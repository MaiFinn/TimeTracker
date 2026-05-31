from dataclasses import asdict, dataclass
from pathlib import Path

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
        project_root = Path(__file__).resolve().parents[2]
        artifacts_dir = project_root / "artifacts"
        file_path = artifacts_dir / "contract.json"

    contract_details = Contract(
        company_name=company_name,
        start_date=start_date,
        salary_per_hour=salary_per_hour,
        hours_per_week=hours_per_week,
    )

    save_json(file_path, asdict(contract_details))