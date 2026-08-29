from datetime import date, time, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.session import Base, get_db
from app.main import app
from app.models import Appointment, Department, Doctor, DoctorSchedule, Patient, Role, User

BOOKING_DATE = date(2026, 9, 1)


@pytest.fixture()
def appointment_client():
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
        doctor_one_user = User(id=2, role=doctor_role, email="doctor.one@example.com", password_hash=password_hash, first_name="One", last_name="Doctor")
        doctor_two_user = User(id=3, role=doctor_role, email="doctor.two@example.com", password_hash=password_hash, first_name="Two", last_name="Doctor")
        patient_one_user = User(id=4, role=patient_role, email="patient.one@example.com", password_hash=password_hash, first_name="One", last_name="Patient")
        patient_two_user = User(id=5, role=patient_role, email="patient.two@example.com", password_hash=password_hash, first_name="Two", last_name="Patient")
        db.add_all([admin_role, doctor_role, patient_role, department, admin, doctor_one_user, doctor_two_user, patient_one_user, patient_two_user])
        db.flush()
        doctor_one = Doctor(id=1, user=doctor_one_user, department=department, specialization="General Medicine", consultation_fee=100, availability_status="AVAILABLE")
        doctor_two = Doctor(id=2, user=doctor_two_user, department=department, specialization="Pediatrics", consultation_fee=80, availability_status="AVAILABLE")
        patient_one = Patient(id=1, user=patient_one_user, status="ACTIVE")
        patient_two = Patient(id=2, user=patient_two_user, status="ACTIVE")
        db.add_all([doctor_one, doctor_two, patient_one, patient_two])
        db.flush()
        db.add_all([
            DoctorSchedule(doctor=doctor_one, day_of_week=1, start_time=time(9), end_time=time(17), appointment_duration=30, break_start=time(13), break_end=time(14), is_available=True),
            DoctorSchedule(doctor=doctor_two, day_of_week=1, start_time=time(9), end_time=time(17), appointment_duration=30, is_available=True),
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


def booking_payload(**overrides):
    payload = {
        "doctor_id": 1,
        "appointment_date": BOOKING_DATE.isoformat(),
        "appointment_time": "10:00:00",
        "reason": "Routine consultation",
    }
    payload.update(overrides)
    return payload


def book(appointment_client, user_id=4, **overrides):
    return appointment_client.post("/api/appointments", headers=headers(user_id, "PATIENT"), json=booking_payload(**overrides))


def test_patient_creates_appointment_with_server_derived_values(appointment_client):
    response = book(appointment_client)
    assert response.status_code == 201
    assert response.json()["patient_id"] == 1
    assert response.json()["status"] == "PENDING"
    assert response.json()["consultation_fee"] == "100.00"
    assert response.json()["payment_status"] == "PENDING"


def test_unauthenticated_and_non_patient_cannot_create(appointment_client):
    assert appointment_client.post("/api/appointments", json=booking_payload()).status_code == 401
    assert appointment_client.post("/api/appointments", headers=headers(2, "DOCTOR"), json=booking_payload()).status_code == 403
    assert appointment_client.post("/api/appointments", headers=headers(1, "ADMIN"), json=booking_payload()).status_code == 403


def test_invalid_doctor_inactive_doctor_and_past_date(appointment_client):
    assert book(appointment_client, doctor_id=999).status_code == 404
    appointment_client.post("/api/doctors/2/deactivate", headers=headers(1, "ADMIN"))
    assert book(appointment_client, doctor_id=2).status_code == 400
    assert book(appointment_client, appointment_date=(date.today() - timedelta(days=1)).isoformat()).status_code == 422


@pytest.mark.parametrize("appointment_time", ["08:30:00", "13:00:00", "13:30:00", "17:00:00"])
def test_invalid_or_break_time_slot_is_rejected(appointment_client, appointment_time):
    response = book(appointment_client, appointment_time=appointment_time)
    assert response.status_code == 400


def test_patient_cannot_book_for_another_patient(appointment_client):
    response = book(appointment_client, patient_id=2)
    assert response.status_code == 403


def test_double_booking_returns_conflict(appointment_client):
    assert book(appointment_client).status_code == 201
    assert book(appointment_client, appointment_time="10:30:00").status_code == 201
    duplicate = book(appointment_client, appointment_time="10:00:00")
    assert duplicate.status_code == 409


def test_patient_views_own_appointments_and_not_another(appointment_client):
    created = book(appointment_client)
    appointment_id = created.json()["id"]
    own = appointment_client.get("/api/appointments/my", headers=headers(4, "PATIENT"))
    assert own.status_code == 200
    assert own.json()["total"] == 1
    assert appointment_client.get(f"/api/appointments/{appointment_id}", headers=headers(5, "PATIENT")).status_code == 403
    assert appointment_client.get("/api/appointments/999", headers=headers(4, "PATIENT")).status_code == 404


def test_doctor_views_own_appointments_only(appointment_client):
    book(appointment_client)
    own = appointment_client.get("/api/appointments/my", headers=headers(2, "DOCTOR"))
    assert own.status_code == 200
    assert own.json()["total"] == 1
    assert appointment_client.get("/api/appointments/1", headers=headers(3, "DOCTOR")).status_code == 403
    assert appointment_client.get("/api/appointments", headers=headers(2, "DOCTOR")).status_code == 403


def test_admin_views_and_filters_all_appointments(appointment_client):
    book(appointment_client)
    second = book(appointment_client, doctor_id=2, appointment_time="10:00:00")
    assert second.status_code == 201
    admin = headers(1, "ADMIN")
    assert appointment_client.get("/api/appointments", headers=admin).json()["total"] == 2
    assert appointment_client.get("/api/appointments?doctor_id=2", headers=admin).json()["total"] == 1
    assert appointment_client.get("/api/appointments?patient_id=1", headers=admin).json()["total"] == 2
    assert appointment_client.get("/api/appointments?status=PENDING", headers=admin).json()["total"] == 2
    assert appointment_client.get(f"/api/appointments?date={BOOKING_DATE.isoformat()}", headers=admin).json()["total"] == 2


def test_doctor_confirm_reject_complete_and_ownership(appointment_client):
    first = book(appointment_client)
    first_id = first.json()["id"]
    confirmed = appointment_client.patch(f"/api/appointments/{first_id}/confirm", headers=headers(2, "DOCTOR"))
    assert confirmed.status_code == 200
    completed = appointment_client.patch(f"/api/appointments/{first_id}/complete", headers=headers(2, "DOCTOR"))
    assert completed.status_code == 200
    assert completed.json()["status"] == "COMPLETED"
    second = book(appointment_client, appointment_time="11:00:00")
    second_id = second.json()["id"]
    assert appointment_client.patch(f"/api/appointments/{second_id}/reject", headers=headers(3, "DOCTOR")).status_code == 403
    assert appointment_client.patch(f"/api/appointments/{second_id}/reject", headers=headers(2, "DOCTOR")).status_code == 200


def test_patient_cancels_and_completed_cannot_cancel(appointment_client):
    first = book(appointment_client)
    cancelled = appointment_client.patch(f"/api/appointments/{first.json()['id']}/cancel", headers=headers(4, "PATIENT"))
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"
    second = book(appointment_client, appointment_time="11:00:00")
    appointment_client.patch(f"/api/appointments/{second.json()['id']}/confirm", headers=headers(2, "DOCTOR"))
    appointment_client.patch(f"/api/appointments/{second.json()['id']}/complete", headers=headers(2, "DOCTOR"))
    assert appointment_client.patch(f"/api/appointments/{second.json()['id']}/cancel", headers=headers(4, "PATIENT")).status_code == 400


def test_invalid_state_transitions_are_rejected(appointment_client):
    appointment = book(appointment_client).json()["id"]
    assert appointment_client.patch(f"/api/appointments/{appointment}/complete", headers=headers(2, "DOCTOR")).status_code == 400
    appointment_client.patch(f"/api/appointments/{appointment}/reject", headers=headers(2, "DOCTOR"))
    assert appointment_client.patch(f"/api/appointments/{appointment}/complete", headers=headers(2, "DOCTOR")).status_code == 400


def test_patient_reschedules_to_valid_slot(appointment_client):
    appointment = book(appointment_client).json()["id"]
    response = appointment_client.patch(
        f"/api/appointments/{appointment}/reschedule",
        headers=headers(4, "PATIENT"),
        json={"appointment_date": BOOKING_DATE.isoformat(), "appointment_time": "12:00:00"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "RESCHEDULED"
    assert response.json()["appointment_time"] == "12:00:00"


def test_reschedule_unavailable_booked_and_other_patient_denied(appointment_client):
    first = book(appointment_client).json()["id"]
    second = book(appointment_client, appointment_time="11:00:00").json()["id"]
    unavailable = appointment_client.patch(
        f"/api/appointments/{first}/reschedule", headers=headers(4, "PATIENT"),
        json={"appointment_date": BOOKING_DATE.isoformat(), "appointment_time": "13:30:00"},
    )
    booked = appointment_client.patch(
        f"/api/appointments/{first}/reschedule", headers=headers(4, "PATIENT"),
        json={"appointment_date": BOOKING_DATE.isoformat(), "appointment_time": "11:00:00"},
    )
    other = appointment_client.patch(
        f"/api/appointments/{second}/reschedule", headers=headers(5, "PATIENT"),
        json={"appointment_date": BOOKING_DATE.isoformat(), "appointment_time": "12:00:00"},
    )
    assert unavailable.status_code == 400
    assert booked.status_code == 409
    assert other.status_code == 403


def test_invalid_appointment_id_and_missing_auth(appointment_client):
    assert appointment_client.get("/api/appointments/0", headers=headers(4, "PATIENT")).status_code == 422
    assert appointment_client.get("/api/appointments/not-an-id", headers=headers(4, "PATIENT")).status_code == 422
    assert appointment_client.patch("/api/appointments/1/cancel").status_code == 401
