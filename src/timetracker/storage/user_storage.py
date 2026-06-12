from datetime import datetime, timezone
from pathlib import Path

from timetracker.storage.sqlite_storage import get_connection


def create_user(
    database_file: Path,
    username: str,
    password_hash: str,
) -> int:
    """Create user and return user id."""

    created_at = datetime.now(timezone.utc).isoformat()

    with get_connection(database_file) as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (
                username,
                password_hash,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                username,
                password_hash,
                created_at,
            ),
        )

        connection.commit()

    return int(cursor.lastrowid)


def get_user_by_username(
    database_file: Path,
    username: str,
) -> dict | None:
    """Return user by username."""

    with get_connection(database_file) as connection:
        row = connection.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            LIMIT 1
            """,
            (username,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)

def authenticate_user(
    database_file: Path,
    username: str,
    password: str,
) -> dict | None:
    """Authenticate user."""

    from timetracker.security import verify_password

    user = get_user_by_username(
        database_file,
        username,
    )

    if user is None:
        return None

    if not verify_password(
        password,
        user["password_hash"],
    ):
        return None

    return user