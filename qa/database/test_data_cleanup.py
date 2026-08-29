from database.db_connection import connection


def delete_test_user(email: str):
    """Delete only an explicitly named test user after dependent data is removed."""
    with connection() as db, db.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE email = %s", (email,))
        db.commit()
