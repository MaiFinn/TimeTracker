import sqlite3
from pathlib import Path


def get_connection(database_file: Path) -> sqlite3.Connection:
    """Create SQLite connection."""

    connection = sqlite3.connect(database_file)
    connection.row_factory = sqlite3.Row

    return connection

def create_work_entry(
    database_file: Path,
    user_id: str,
    date: str,
    start_time: str,
    end_time: str,
    total_time: str,
    entry_status: str,
    note: str = "",
) -> int:
    """Insert work entry into database and return its id."""

    with get_connection(database_file) as connection:
        cursor = connection.execute(
            """
            INSERT INTO work_entries (
                user_id,
                date,
                start_time,
                end_time,
                total_time,
                entry_status,
                note
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                date,
                start_time,
                end_time,
                total_time,
                entry_status,
                note,
            ),
        )

        connection.commit()

    return int(cursor.lastrowid)


def load_work_entries(
    database_file: Path,
    user_id: str,
) -> list[dict]:
    """Load all work entries for a user."""

    with get_connection(database_file) as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM work_entries
            WHERE user_id = ?
            ORDER BY date
            """,
            (user_id,),
        ).fetchall()

    entries = [dict(row) for row in rows]

    for entry in entries:
        entry["attachments"] = load_attachments(
            database_file,
            entry["id"],
        )

    return entries

def save_contract(
    database_file: Path,
    user_id: str,
    contract: dict,
) -> None:
    """Save contract for a user."""

    with get_connection(database_file) as connection:
        connection.execute(
            """
            DELETE FROM contracts
            WHERE user_id = ?
            """,
            (user_id,),
        )

        connection.execute(
            """
            INSERT INTO contracts (
                user_id,
                company_name,
                start_date,
                salary_per_hour,
                hours_per_week
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                contract["company_name"],
                contract["start_date"],
                float(contract["salary_per_hour"]),
                float(contract["hours_per_week"]),
            ),
        )

        connection.commit()


def load_contract(
    database_file: Path,
    user_id: str,
) -> dict | None:
    """Load contract for a user."""

    with get_connection(database_file) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM contracts
            WHERE user_id = ?
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)

def count_work_entries(
    database_file: Path,
    user_id: str,
) -> int:
    """Count work entries for a user."""

    with get_connection(database_file) as connection:
        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM work_entries
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    return int(result[0])

def add_attachment(
    database_file: Path,
    work_entry_id: int,
    file_name: str,
    file_path: str,
) -> None:
    """Add attachment to work entry."""

    with get_connection(database_file) as connection:
        connection.execute(
            """
            INSERT INTO attachments (
                work_entry_id,
                file_name,
                file_path
            )
            VALUES (?, ?, ?)
            """,
            (
                work_entry_id,
                file_name,
                file_path,
            ),
        )

        connection.commit()

def load_attachments(
    database_file: Path,
    work_entry_id: int,
) -> list[dict]:
    """Load attachments for work entry."""

    with get_connection(database_file) as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM attachments
            WHERE work_entry_id = ?
            """,
            (work_entry_id,),
        ).fetchall()

    return [dict(row) for row in rows]

def delete_attachment(
    database_file: Path,
    attachment_id: int,
) -> None:
    """Delete attachment."""

    with get_connection(database_file) as connection:
        connection.execute(
            """
            DELETE FROM attachments
            WHERE id = ?
            """,
            (attachment_id,),
        )

        connection.commit()

def update_work_entry(
    database_file: Path,
    work_entry_id: int,
    date: str,
    start_time: str,
    end_time: str,
    total_time: str,
    entry_status: str,
    note: str,
) -> None:
    """Update work entry."""

    with get_connection(database_file) as connection:
        connection.execute(
            """
            UPDATE work_entries
            SET
                date = ?,
                start_time = ?,
                end_time = ?,
                total_time = ?,
                entry_status = ?,
                note = ?
            WHERE id = ?
            """,
            (
                date,
                start_time,
                end_time,
                total_time,
                entry_status,
                note,
                work_entry_id,
            ),
        )

        connection.commit()


def delete_work_entry(
    database_file: Path,
    work_entry_id: int,
) -> None:
    """Delete work entry and related attachments."""

    with get_connection(database_file) as connection:
        connection.execute(
            """
            DELETE FROM attachments
            WHERE work_entry_id = ?
            """,
            (work_entry_id,),
        )

        connection.execute(
            """
            DELETE FROM work_entries
            WHERE id = ?
            """,
            (work_entry_id,),
        )

        connection.commit()