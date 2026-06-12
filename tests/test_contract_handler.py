from timetracker.contract_handler import create_contract
from timetracker.database.schema import initialize_database
from timetracker.storage.sqlite_storage import load_contract


def test_create_contract(tmp_path) -> None:
    database_file = tmp_path / "test.db"
    initialize_database(database_file)

    create_contract(
        company_name="test_company",
        start_date="2026-02-10",
        salary_per_hour=20,
        hours_per_week=5,
        user_id="test_user",
        database_file=database_file,
    )

    contract = load_contract(database_file, "test_user")

    assert contract is not None
    assert contract["company_name"] == "test_company"
    assert contract["start_date"] == "2026-02-10"
    assert contract["salary_per_hour"] == 20
    assert contract["hours_per_week"] == 5