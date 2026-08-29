import pytest
from datetime import date, time
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.session import Base, get_db
from app.main import app
from app.models import Appointment, Department, Doctor, Patient, Role, User


@pytest.fixture()
def business_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        admin_role = Role(id=1, name="ADMIN")
        doctor_role = Role(id=2, name="DOCTOR")
        patient_role = Role(id=3, name="PATIENT")
        department = Department(id=1, name="General Medicine")
        password = hash_password("ValidPass1!")
        admin = User(id=1, role=admin_role, email="admin@example.com", password_hash=password, first_name="Admin", last_name="User")
        doctor_user = User(id=2, role=doctor_role, email="doctor@example.com", password_hash=password, first_name="Doctor", last_name="User")
        patient_user = User(id=3, role=patient_role, email="patient@example.com", password_hash=password, first_name="Patient", last_name="User")
        db.add_all([admin_role, doctor_role, patient_role, department, admin, doctor_user, patient_user])
        db.flush()
        doctor = Doctor(id=1, user=doctor_user, department=department, specialization="General Medicine", consultation_fee=100, availability_status="AVAILABLE")
        patient = Patient(id=1, user=patient_user, status="ACTIVE")
        db.add_all([doctor, patient])
        db.flush()
        appointment = Appointment(id=1, patient=patient, doctor=doctor, appointment_date=date(2026, 9, 1), appointment_time=time(10), status="COMPLETED", consultation_fee=Decimal("100.00"), payment_status="PENDING")
        db.add(appointment)
        db.commit()

    def override_get_db():
        with SessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def token_headers(user_id: int, role: str) -> dict[str, str]:
    token, _ = create_access_token(user_id, role)
    return {"Authorization": f"Bearer {token}"}
