from app.core.config import Settings
from app.db.session import Base
from app.models import (
    Appointment,
    Bill,
    Department,
    Doctor,
    DoctorSchedule,
    MedicalRecord,
    Notification,
    Patient,
    Payment,
    Prescription,
    PrescriptionItem,
    Role,
    User,
)


def test_database_configuration_builds_mysql_url():
    settings = Settings(
        db_host="db.example.test",
        db_port=3307,
        db_name="demo",
        db_user="demo_user",
        db_password="demo_password",
    )

    assert settings.sqlalchemy_database_url == (
        "mysql+pymysql://demo_user:demo_password@db.example.test:3307/demo"
    )


def test_expected_tables_are_registered():
    expected_tables = {
        "roles", "users", "patients", "departments", "doctors",
        "doctor_schedules", "appointments", "medical_records",
        "prescriptions", "prescription_items", "bills", "payments",
        "notifications",
    }

    assert expected_tables == set(Base.metadata.tables)


def test_relationships_and_foreign_keys_are_configured():
    assert User.role.property.mapper.class_ is Role
    assert Patient.user.property.mapper.class_ is User
    assert Doctor.department.property.mapper.class_ is Department
    assert DoctorSchedule.doctor.property.mapper.class_ is Doctor
    assert Appointment.patient.property.mapper.class_ is Patient
    assert Appointment.doctor.property.mapper.class_ is Doctor
    assert MedicalRecord.appointment.property.mapper.class_ is Appointment
    assert Prescription.appointment.property.mapper.class_ is Appointment
    assert PrescriptionItem.prescription.property.mapper.class_ is Prescription
    assert Bill.appointment.property.mapper.class_ is Appointment
    assert Payment.bill.property.mapper.class_ is Bill
    assert Notification.user.property.mapper.class_ is User

    assert "users" in {foreign_key.column.table.name for foreign_key in Patient.__table__.foreign_keys}
    assert "doctors" in {foreign_key.column.table.name for foreign_key in Appointment.__table__.foreign_keys}
    assert "bills" in {foreign_key.column.table.name for foreign_key in Payment.__table__.foreign_keys}
