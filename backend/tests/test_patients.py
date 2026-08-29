from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.session import Base, get_db
from app.main import app
from app.models import Patient, Role, User


@pytest.fixture()
def patient_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        admin_role = Role(id=1, name="ADMIN")
        patient_role = Role(id=3, name="PATIENT")
        doctor_role = Role(id=2, name="DOCTOR")
        admin = User(id=1, role=admin_role, email="admin@example.com", password_hash=hash_password("AdminPass1!"), first_name="Admin", last_name="User")
        patient_one = User(id=2, role=patient_role, email="one@example.com", phone="5551000001", password_hash=hash_password("PatientPass1!"), first_name="One", last_name="Patient")
        patient_two = User(id=3, role=patient_role, email="two@example.com", phone="5551000002", password_hash=hash_password("PatientPass1!"), first_name="Two", last_name="Patient")
        doctor = User(id=4, role=doctor_role, email="doctor@example.com", password_hash=hash_password("DoctorPass1!"), first_name="Doctor", last_name="User")
        db.add_all([admin_role, patient_role, doctor_role, admin, patient_one, patient_two, doctor])
        db.flush()
        db.add_all([
            Patient(id=1, user=patient_one, date_of_birth=date(1990, 1, 1), gender="FEMALE", blood_group="O+", status="ACTIVE"),
            Patient(id=2, user=patient_two, date_of_birth=date(1985, 2, 2), gender="MALE", blood_group="A+", status="ACTIVE"),
        ])
        db.commit()

    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def headers(user_id: int, role: str) -> dict[str, str]:
    token, _ = create_access_token(user_id, role)
    return {"Authorization": f"Bearer {token}"}


def test_patient_can_access_own_profile(patient_client):
    response = patient_client.get("/api/patients/me", headers=headers(2, "PATIENT"))
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["email"] == "one@example.com"
    assert "password_hash" not in response.text

    detail = patient_client.get("/api/patients/1", headers=headers(2, "PATIENT"))
    assert detail.status_code == 200


def test_patient_cannot_access_another_patient(patient_client):
    response = patient_client.get("/api/patients/2", headers=headers(2, "PATIENT"))
    assert response.status_code == 403


def test_admin_can_view_search_and_manage_patients(patient_client):
    admin_headers = headers(1, "ADMIN")
    response = patient_client.get("/api/patients/2", headers=admin_headers)
    assert response.status_code == 200
    search = patient_client.get("/api/patients?query=Two", headers=admin_headers)
    assert search.status_code == 200
    assert [item["id"] for item in search.json()] == [2]


def test_unauthenticated_patient_access_is_rejected(patient_client):
    assert patient_client.get("/api/patients/1").status_code == 401
    assert patient_client.get("/api/patients").status_code == 401


def test_invalid_and_missing_patient_ids(patient_client):
    admin_headers = headers(1, "ADMIN")
    assert patient_client.get("/api/patients/0", headers=admin_headers).status_code == 422
    assert patient_client.get("/api/patients/not-an-id", headers=admin_headers).status_code == 422
    assert patient_client.get("/api/patients/999", headers=admin_headers).status_code == 404


def test_patient_can_update_own_profile(patient_client):
    response = patient_client.patch(
        "/api/patients/1",
        headers=headers(2, "PATIENT"),
        json={"address": "Demo address", "gender": "OTHER", "blood_group": "AB+"},
    )
    assert response.status_code == 200
    assert response.json()["address"] == "Demo address"
    assert response.json()["gender"] == "OTHER"
    assert response.json()["blood_group"] == "AB+"


def test_patient_cannot_update_another_profile(patient_client):
    response = patient_client.patch(
        "/api/patients/2",
        headers=headers(2, "PATIENT"),
        json={"address": "Unauthorized"},
    )
    assert response.status_code == 403


@pytest.mark.parametrize(
    "payload",
    [
        {"date_of_birth": "2999-01-01"},
        {"gender": "INVALID"},
        {"blood_group": "X+"},
        {"phone": "123"},
        {"email": "not-an-email"},
    ],
)
def test_invalid_patient_update_returns_422(patient_client, payload):
    response = patient_client.patch(
        "/api/patients/1",
        headers=headers(2, "PATIENT"),
        json=payload,
    )
    assert response.status_code == 422


def test_duplicate_email_or_phone_returns_conflict(patient_client):
    admin_headers = headers(1, "ADMIN")
    email_response = patient_client.patch(
        "/api/patients/2",
        headers=admin_headers,
        json={"email": "one@example.com"},
    )
    assert email_response.status_code == 409
    phone_response = patient_client.patch(
        "/api/patients/2",
        headers=admin_headers,
        json={"phone": "5551000001"},
    )
    assert phone_response.status_code == 409


def test_admin_can_deactivate_patient(patient_client):
    response = patient_client.post("/api/patients/2/deactivate", headers=headers(1, "ADMIN"))
    assert response.status_code == 200
    assert response.json()["status"] == "INACTIVE"
    assert patient_client.get("/api/patients/2", headers=headers(3, "PATIENT")).status_code == 401


def test_only_admin_can_deactivate_patient(patient_client):
    response = patient_client.post("/api/patients/1/deactivate", headers=headers(2, "PATIENT"))
    assert response.status_code == 403
