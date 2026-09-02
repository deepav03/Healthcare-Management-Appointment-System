from datetime import date, time, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.session import Base, get_db
from app.main import app
from app.models import Department, Doctor, DoctorSchedule, Role, User
from app.services.schedule_service import generate_available_slots


def next_weekday_date(target_weekday: int) -> date:
    today = date.today()
    days_until_target = (target_weekday - today.weekday()) % 7
    if days_until_target == 0:
        days_until_target = 7
    return today + timedelta(days=days_until_target)


@pytest.fixture()
def schedule_client():
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
        department = Department(id=1, name="General Medicine")
        password_hash = hash_password("ValidPass1!")
        admin = User(id=1, role=admin_role, email="admin@example.com", password_hash=password_hash, first_name="Admin", last_name="User")
        doctor_one = User(id=2, role=doctor_role, email="doctor.one@example.com", password_hash=password_hash, first_name="One", last_name="Doctor")
        doctor_two = User(id=3, role=doctor_role, email="doctor.two@example.com", password_hash=password_hash, first_name="Two", last_name="Doctor")
        patient = User(id=4, role=patient_role, email="patient@example.com", password_hash=password_hash, first_name="Patient", last_name="User")
        db.add_all([admin_role, doctor_role, patient_role, department, admin, doctor_one, doctor_two, patient])
        db.flush()
        db.add_all([
            Doctor(id=1, user=doctor_one, department=department, specialization="General Medicine", consultation_fee=100, availability_status="AVAILABLE"),
            Doctor(id=2, user=doctor_two, department=department, specialization="Pediatrics", consultation_fee=80, availability_status="AVAILABLE"),
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


def schedule_payload(**overrides):
    payload = {
        "day_of_week": 1,
        "start_time": "09:00:00",
        "end_time": "17:00:00",
        "appointment_duration": 30,
        "break_start": "13:00:00",
        "break_end": "14:00:00",
        "is_available": True,
    }
    payload.update(overrides)
    return payload


def test_admin_creates_schedule(schedule_client):
    response = schedule_client.post("/api/doctors/1/schedules", headers=headers(1, "ADMIN"), json=schedule_payload())
    assert response.status_code == 201
    assert response.json()["doctor_id"] == 1
    assert response.json()["day_of_week"] == 1


def test_doctor_creates_own_schedule_and_patient_cannot(schedule_client):
    own = schedule_client.post("/api/doctors/1/schedules", headers=headers(2, "DOCTOR"), json=schedule_payload())
    assert own.status_code == 201
    patient = schedule_client.post("/api/doctors/1/schedules", headers=headers(4, "PATIENT"), json=schedule_payload(day_of_week=2))
    assert patient.status_code == 403


def test_invalid_doctor_and_unauthorized_schedule_access(schedule_client):
    assert schedule_client.get("/api/doctors/999/schedules", headers=headers(1, "ADMIN")).status_code == 404
    assert schedule_client.get("/api/doctors/0/schedules", headers=headers(1, "ADMIN")).status_code == 422
    assert schedule_client.get("/api/doctors/1/schedules").status_code == 401
    assert schedule_client.get("/api/doctors/2/schedules", headers=headers(2, "DOCTOR")).status_code == 403


def test_invalid_schedule_times_and_duration(schedule_client):
    admin = headers(1, "ADMIN")
    assert schedule_client.post("/api/doctors/1/schedules", headers=admin, json=schedule_payload(start_time="18:00:00", end_time="09:00:00")).status_code == 422
    assert schedule_client.post("/api/doctors/1/schedules", headers=admin, json=schedule_payload(appointment_duration=0, day_of_week=2)).status_code == 422
    assert schedule_client.post("/api/doctors/1/schedules", headers=admin, json=schedule_payload(break_start="17:00:00", break_end="18:00:00", day_of_week=2)).status_code == 422
    assert schedule_client.post("/api/doctors/1/schedules", headers=admin, json=schedule_payload(break_start="13:00:00", break_end=None, day_of_week=3)).status_code == 422


def test_overlapping_and_duplicate_schedules_return_conflict(schedule_client):
    admin = headers(1, "ADMIN")
    assert schedule_client.post("/api/doctors/1/schedules", headers=admin, json=schedule_payload()).status_code == 201
    overlap = schedule_client.post("/api/doctors/1/schedules", headers=admin, json=schedule_payload(start_time="12:00:00", end_time="15:00:00"))
    duplicate = schedule_client.post("/api/doctors/1/schedules", headers=admin, json=schedule_payload())
    assert overlap.status_code == 409
    assert duplicate.status_code == 409
    non_overlap = schedule_client.post("/api/doctors/1/schedules", headers=admin, json=schedule_payload(start_time="18:00:00", end_time="20:00:00", break_start=None, break_end=None))
    assert non_overlap.status_code == 201


def test_update_and_delete_schedule(schedule_client):
    doctor = headers(2, "DOCTOR")
    created = schedule_client.post("/api/doctors/1/schedules", headers=doctor, json=schedule_payload())
    schedule_id = created.json()["id"]
    updated = schedule_client.patch(
        f"/api/schedules/{schedule_id}",
        headers=doctor,
        json=schedule_payload(start_time="10:00:00", end_time="16:00:00", break_start="12:00:00", break_end="13:00:00"),
    )
    assert updated.status_code == 200
    assert updated.json()["start_time"] == "10:00:00"
    deleted = schedule_client.delete(f"/api/schedules/{schedule_id}", headers=doctor)
    assert deleted.status_code == 204
    assert schedule_client.get("/api/doctors/1/schedules", headers=headers(1, "ADMIN")).json() == []


def test_doctor_cannot_modify_another_doctors_schedule(schedule_client):
    admin = headers(1, "ADMIN")
    created = schedule_client.post("/api/doctors/1/schedules", headers=admin, json=schedule_payload())
    schedule_id = created.json()["id"]
    doctor_two = headers(3, "DOCTOR")
    assert schedule_client.patch(f"/api/schedules/{schedule_id}", headers=doctor_two, json=schedule_payload()).status_code == 403
    assert schedule_client.delete(f"/api/schedules/{schedule_id}", headers=doctor_two).status_code == 403


def test_patient_views_active_doctor_availability(schedule_client):
    admin = headers(1, "ADMIN")
    schedule_client.post("/api/doctors/1/schedules", headers=admin, json=schedule_payload())
    patient = headers(4, "PATIENT")
    weekly = schedule_client.get("/api/doctors/1/availability", headers=patient)
    assert weekly.status_code == 200
    availability_date = next_weekday_date(1)
    daily = schedule_client.get(f"/api/doctors/1/availability/{availability_date.isoformat()}", headers=patient)
    assert daily.status_code == 200
    assert daily.json()["available_slots"] == [
        "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
        "14:00", "14:30", "15:00", "15:30", "16:00", "16:30",
    ]


def test_inactive_doctor_availability_is_hidden(schedule_client):
    admin = headers(1, "ADMIN")
    schedule_client.post("/api/doctors/2/schedules", headers=admin, json=schedule_payload())
    schedule_client.post("/api/doctors/2/deactivate", headers=admin)
    availability_date = next_weekday_date(1)
    response = schedule_client.get(f"/api/doctors/2/availability/{availability_date.isoformat()}", headers=headers(4, "PATIENT"))
    assert response.status_code == 404


def test_invalid_and_past_availability_dates(schedule_client):
    patient = headers(4, "PATIENT")
    assert schedule_client.get("/api/doctors/1/availability/not-a-date", headers=patient).status_code == 422
    past = (date.today() - timedelta(days=1)).isoformat()
    assert schedule_client.get(f"/api/doctors/1/availability/{past}", headers=patient).status_code == 400


def test_generated_slots_exclude_break_and_booked_slots():
    schedule = DoctorSchedule(
        day_of_week=1,
        start_time=time(9),
        end_time=time(17),
        appointment_duration=30,
        break_start=time(13),
        break_end=time(14),
        is_available=True,
    )
    future_tuesday = next_weekday_date(1)
    slots = generate_available_slots([schedule], future_tuesday, booked_slots=["09:30", time(14, 30)])
    assert "13:00" not in slots
    assert "13:30" not in slots
    assert "09:30" not in slots
    assert "14:00" in slots


def test_unavailable_schedule_generates_no_slots():
    schedule = DoctorSchedule(
        day_of_week=1,
        start_time=time(9),
        end_time=time(17),
        appointment_duration=30,
        is_available=False,
    )
    assert generate_available_slots([schedule], next_weekday_date(1)) == []
