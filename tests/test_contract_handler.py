from timetracker.contract_handler import create_contract
from pathlib import Path
import json

def test_create_contract(tmp_path) -> None:

    company_name="test_company"
    start_date="2026-02-10"
    salary_per_hour=20
    hours_per_week=5
    file_path=tmp_path / "contract.json"

    create_contract(company_name, start_date, salary_per_hour, hours_per_week, file_path)

    assert file_path.exists()

    with open(file_path, "r") as f:
        data = json.load(f)
    
    assert data == {
        "company_name": "test_company",
        "start_date": "2026-02-10",
        "salary_per_hour": 20,
        "hours_per_week": 5,
    }