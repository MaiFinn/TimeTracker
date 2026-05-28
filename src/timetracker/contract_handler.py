import json
from dataclasses import asdict, dataclass
from pathlib import Path

@dataclass
class Contract:
    "Container class for contract infos."

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
    """
    Create a new contract file.

    Args:
        company_name (str): Name of the company
        start_date (str): Contract starting date
        salar_per_hour (float): Hourly compensation
        hours_per_week (float): Working hours per week
    """
    if file_path is None:

        PROJECT_ROOT = Path(__file__).resolve().parents[2]
        ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
        ARTIFACTS_DIR.mkdir(exist_ok=True)
        file_path = ARTIFACTS_DIR / "contract.json"
    
    contract_details = Contract(
    company_name=company_name,
    start_date=start_date,
    salary_per_hour=salary_per_hour,
    hours_per_week=hours_per_week
    )

    contract_dict = asdict(contract_details)

    with open(file_path, "w") as f:
        json.dump(contract_dict, f)