import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.db.session import Base, get_db
from app.main import app
from app.models import Role, User


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        roles = [
            Role(id=1, name="ADMIN"),
            Role(id=2, name="DOCTOR"),
            Role(id=3, name="PATIENT"),
        ]
        db.add_all(roles)
        db.add_all(
            [
                User(id=1, role=roles[0], email="admin@example.com", password_hash=hash_password("AdminPass1!"), first_name="Admin", last_name="User"),
                User(id=2, role=roles[1], email="doctor@example.com", password_hash=hash_password("DoctorPass1!"), first_name="Doctor", last_name="User"),
                User(id=3, role=roles[2], email="patient@example.com", password_hash=hash_password("PatientPass1!"), first_name="Patient", last_name="User"),
                User(id=4, role=roles[2], email="inactive@example.com", password_hash=hash_password("PatientPass1!"), first_name="Inactive", last_name="User", is_active=False),
            ]
        )
        db.commit()

    def override_get_db():
        with TestingSessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def token_for(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_successful_registration_creates_patient_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "first_name": "New",
            "last_name": "Patient",
            "email": "new.patient@example.com",
            "phone": "5550001111",
            "password": "StrongPass1!",
            "password_confirmation": "StrongPass1!",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "PATIENT"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


def test_duplicate_registration_returns_conflict(client):
    payload = {
        "first_name": "New",
        "last_name": "Patient",
        "email": "patient@example.com",
        "phone": "5550002222",
        "password": "StrongPass1!",
        "password_confirmation": "StrongPass1!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


def test_duplicate_phone_returns_conflict(client):
    first = {
        "first_name": "First",
        "last_name": "Patient",
        "email": "first@example.com",
        "phone": "5550003333",
        "password": "StrongPass1!",
        "password_confirmation": "StrongPass1!",
    }
    second = {**first, "email": "second@example.com"}
    assert client.post("/api/auth/register", json=first).status_code == 201
    assert client.post("/api/auth/register", json=second).status_code == 409


@pytest.mark.parametrize(
    "field, value",
    [
        ("email", "not-an-email"),
        ("password", "weakpass"),
    ],
)
def test_invalid_registration_data_returns_unprocessable_entity(client, field, value):
    payload = {
        "first_name": "New",
        "last_name": "Patient",
        "email": "valid@example.com",
        "phone": "5550004444",
        "password": "StrongPass1!",
        "password_confirmation": "StrongPass1!",
    }
    payload[field] = value
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_password_mismatch_returns_unprocessable_entity(client):
    response = client.post(
        "/api/auth/register",
        json={
            "first_name": "New",
            "last_name": "Patient",
            "email": "mismatch@example.com",
            "phone": "5550005555",
            "password": "StrongPass1!",
            "password_confirmation": "DifferentPass1!",
        },
    )
    assert response.status_code == 422


def test_successful_login_returns_jwt(client):
    response = client.post("/api/auth/login", json={"email": "patient@example.com", "password": "PatientPass1!"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]
    assert response.json()["expires_in"] > 0


@pytest.mark.parametrize(
    "email, password",
    [("patient@example.com", "WrongPass1!"), ("unknown@example.com", "PatientPass1!")],
)
def test_invalid_login_returns_unauthorized(client, email, password):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 401
    assert password not in response.text
    assert "password_hash" not in response.text


def test_inactive_login_returns_unauthorized(client):
    response = client.post("/api/auth/login", json={"email": "inactive@example.com", "password": "PatientPass1!"})
    assert response.status_code == 401


def test_valid_token_and_me_endpoint(client):
    token = token_for(client, "patient@example.com", "PatientPass1!")
    response = client.get("/api/auth/me", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json() == {
        "id": 3,
        "email": "patient@example.com",
        "first_name": "Patient",
        "last_name": "User",
        "role": "PATIENT",
        "is_active": True,
    }


def test_missing_and_invalid_tokens_return_unauthorized(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers=auth_headers("not-a-token")).status_code == 401


def test_role_authorization_allows_only_matching_role(client):
    admin = auth_headers(token_for(client, "admin@example.com", "AdminPass1!"))
    doctor = auth_headers(token_for(client, "doctor@example.com", "DoctorPass1!"))
    patient = auth_headers(token_for(client, "patient@example.com", "PatientPass1!"))

    assert client.get("/api/auth/admin-check", headers=admin).status_code == 200
    assert client.get("/api/auth/doctor-check", headers=doctor).status_code == 200
    assert client.get("/api/auth/patient-check", headers=patient).status_code == 200
    assert client.get("/api/auth/admin-check", headers=patient).status_code == 403
    assert client.get("/api/auth/doctor-check", headers=admin).status_code == 403
    assert client.get("/api/auth/patient-check", headers=doctor).status_code == 403


def test_logout_is_stateless_acknowledgement(client):
    token = token_for(client, "patient@example.com", "PatientPass1!")
    response = client.post("/api/auth/logout", headers=auth_headers(token))
    assert response.status_code == 200
    assert "discard" in response.json()["message"]
