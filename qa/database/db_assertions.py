from database.db_connection import can_connect


def require_live_mysql():
    if not can_connect():
        raise RuntimeError("Live MySQL is unavailable or healthcare_user credentials are invalid")


def assert_row_value(row: dict, column: str, expected):
    assert row is not None, "Expected database row was not found"
    assert row[column] == expected
