from database.db_connection import connection


def fetch_patient_by_id(patient_id: int):
    with connection() as db, db.cursor() as cursor:
        cursor.execute("SELECT id, user_id, status FROM patients WHERE id = %s", (patient_id,))
        return cursor.fetchone()


def fetch_appointment(appointment_id: int):
    with connection() as db, db.cursor() as cursor:
        cursor.execute("SELECT id, patient_id, doctor_id, appointment_date, appointment_time, status FROM appointments WHERE id = %s", (appointment_id,))
        return cursor.fetchone()


def count_rows(table_name: str) -> int:
    allowed_tables = {"users", "patients", "doctors", "appointments", "medical_records", "prescriptions", "prescription_items", "bills", "payments", "notifications"}
    if table_name not in allowed_tables:
        raise ValueError("Unsupported table")
    with connection() as db, db.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) AS total FROM `{table_name}`")
        return cursor.fetchone()["total"]
