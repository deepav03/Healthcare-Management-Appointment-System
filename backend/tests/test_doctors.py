from datetime import datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.session import Base, get_db
from app.main import app
from app.models import Department, Doctor, Role, User


@pytest.fixture()
def doctor_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        admin_role = Role(id=1, name="ADMIN")
        doctor_role = Role(id=2, name="DOCTOR")
        patient_role = Role(id=3, name="PATIENT")
        departments = [
            Department(id=1, name="General Medicine"),
            Department(id=2, name="Pediatrics"),
        ]
        password_hash = hash_password("ValidPass1!")
        users = [
            User(id=1, role=admin_role, email="admin@example.com", password_hash=password_hash, first_name="Admin", last_name="User"),
            User(id=2, role=doctor_role, email="doctor.one@example.com", phone="5552000001", password_hash=password_hash, first_name="One", last_name="Doctor"),
            User(id=3, role=doctor_role, email="doctor.two@example.com", phone="5552000002", password_hash=password_hash, first_name="Two", last_name="Doctor"),
            User(id=4, role=patient_role, email="patient@example.com", password_hash=password_hash, first_name="Patient", last_name="User"),
        ]
        db.add_all([admin_role, doctor_role, patient_role, *departments, *users])
        db.flush()
        db.add_all([
            Doctor(id=1, user=users[1], department=departments[0], specialization="Cardiology", qualification="MD", experience=10, consultation_fee=100, availability_status="AVAILABLE"),
            Doctor(id=2, user=users[2], department=departments[1], specialization="Pediatrics", qualification="MD", experience=8, consultation_fee=80, availability_status="AVAILABLE"),
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


def create_payload(**overrides):
    payload = {
        "first_name": "New",
        "last_name": "Doctor",
        "email": "new.doctor@example.com",
        "phone": "5552000099",
        "specialization": "Neurology",
        "qualification": "MD, Neurology",
        "experience": 7,
        "department_id": 1,
        "consultation_fee": "125.00",
        "availability_status": "AVAILABLE",
    }
    payload.update(overrides)
    return payload


def test_admin_creates_doctor(doctor_client):
    response = doctor_client.post("/api/doctors", headers=headers(1, "ADMIN"), json=create_payload())
    assert response.status_code == 201
    assert response.json()["specialization"] == "Neurology"
    assert response.json()["is_active"] is True
    assert "password_hash" not in response.text


def test_non_admin_cannot_create_doctor(doctor_client):
    response = doctor_client.post("/api/doctors", headers=headers(4, "PATIENT"), json=create_payload())
    assert response.status_code == 403
    assert doctor_client.post("/api/doctors", json=create_payload()).status_code == 401


def test_get_doctor_and_invalid_id(doctor_client):
    response = doctor_client.get("/api/doctors/1", headers=headers(4, "PATIENT"))
    assert response.status_code == 200
    assert response.json()["department_name"] == "General Medicine"
    assert doctor_client.get("/api/doctors/0", headers=headers(1, "ADMIN")).status_code == 422
    assert doctor_client.get("/api/doctors/not-an-id", headers=headers(1, "ADMIN")).status_code == 422
    assert doctor_client.get("/api/doctors/999", headers=headers(1, "ADMIN")).status_code == 404


def test_list_search_and_filters(doctor_client):
    admin = headers(1, "ADMIN")
    assert len(doctor_client.get("/api/doctors", headers=admin).json()) == 2
    assert [item["id"] for item in doctor_client.get("/api/doctors?search=Cardio", headers=admin).json()] == [1]
    assert [item["id"] for item in doctor_client.get("/api/doctors?specialization=Pediatrics", headers=admin).json()] == [2]
    assert [item["id"] for item in doctor_client.get("/api/doctors?department=2", headers=admin).json()] == [2]


def test_doctor_can_update_own_profile_but_not_another(doctor_client):
    own = doctor_client.patch(
        "/api/doctors/1",
        headers=headers(2, "DOCTOR"),
        json={"specialization": "Internal Medicine", "consultation_fee": "115.00"},
    )
    assert own.status_code == 200
    assert own.json()["specialization"] == "Internal Medicine"
    other = doctor_client.patch(
        "/api/doctors/2",
        headers=headers(2, "DOCTOR"),
        json={"specialization": "Unauthorized"},
    )
    assert other.status_code == 403


def test_patient_can_view_and_search_but_not_modify(doctor_client):
    patient = headers(4, "PATIENT")
    assert doctor_client.get("/api/doctors?search=Cardio", headers=patient).status_code == 200
    assert doctor_client.get("/api/doctors/1", headers=patient).status_code == 200
    assert doctor_client.patch("/api/doctors/1", headers=patient, json={"qualification": "Nope"}).status_code == 403


@pytest.mark.parametrize(
    "field, value",
    [
        ("consultation_fee", "-1.00"),
        ("experience", -1),
        ("department_id", 999),
        ("specialization", ""),
        ("email", "not-an-email"),
        ("phone", "123"),
    ],
)
def test_invalid_create_data(doctor_client, field, value):
    response = doctor_client.post("/api/doctors", headers=headers(1, "ADMIN"), json=create_payload(**{field: value}))
    assert response.status_code in {404, 422}


def test_duplicate_email_and_phone(doctor_client):
    admin = headers(1, "ADMIN")
    assert doctor_client.post("/api/doctors", headers=admin, json=create_payload(email="doctor.one@example.com")).status_code == 409
    assert doctor_client.post("/api/doctors", headers=admin, json=create_payload(phone="5552000001")).status_code == 409


def test_invalid_department_returns_not_found(doctor_client):
    response = doctor_client.post("/api/doctors", headers=headers(1, "ADMIN"), json=create_payload(department_id=999))
    assert response.status_code == 404


def test_deactivate_excludes_doctor_from_patient_search(doctor_client):
    admin = headers(1, "ADMIN")
    response = doctor_client.post("/api/doctors/1/deactivate", headers=admin)
    assert response.status_code == 200
    assert response.json()["is_active"] is False
    assert response.json()["availability_status"] == "UNAVAILABLE"
    assert doctor_client.get("/api/doctors?search=Cardio", headers=headers(4, "PATIENT")).json() == []
    assert doctor_client.get("/api/doctors/1", headers=headers(4, "PATIENT")).status_code == 404


def test_only_admin_can_activate_or_deactivate(doctor_client):
    assert doctor_client.post("/api/doctors/1/deactivate", headers=headers(2, "DOCTOR")).status_code == 403
    assert doctor_client.post("/api/doctors/1/activate", headers=headers(2, "DOCTOR")).status_code == 403


def test_admin_can_activate_doctor(doctor_client):
    admin = headers(1, "ADMIN")
    doctor_client.post("/api/doctors/1/deactivate", headers=admin)
    response = doctor_client.post("/api/doctors/1/activate", headers=admin)
    assert response.status_code == 200
    assert response.json()["is_active"] is True
    assert response.json()["availability_status"] == "AVAILABLE"
