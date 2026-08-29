from datetime import date, datetime, time
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Appointment, AppointmentStatus, Doctor, Patient, User
from app.schemas.appointment import AppointmentCreateRequest, AppointmentRescheduleRequest
from app.services.schedule_service import generate_available_slots


class AppointmentNotFoundError(Exception):
    pass


class AppointmentConflictError(Exception):
    pass


class AppointmentValidationError(Exception):
    pass


def appointment_query():
    return select(Appointment).options(
        joinedload(Appointment.patient).joinedload(Patient.user),
        joinedload(Appointment.doctor).joinedload(Doctor.user),
    )


def get_appointment(db: Session, appointment_id: int) -> Appointment | None:
    return db.scalar(appointment_query().where(Appointment.id == appointment_id))


def list_appointments(
    db: Session,
    patient_id: int | None = None,
    doctor_id: int | None = None,
    appointment_date: date | None = None,
    appointment_status: str | None = None,
) -> list[Appointment]:
    statement = appointment_query()
    if patient_id is not None:
        statement = statement.where(Appointment.patient_id == patient_id)
    if doctor_id is not None:
        statement = statement.where(Appointment.doctor_id == doctor_id)
    if appointment_date is not None:
        statement = statement.where(Appointment.appointment_date == appointment_date)
    if appointment_status is not None:
        statement = statement.where(Appointment.status == appointment_status.upper())
    return list(db.scalars(statement.order_by(Appointment.appointment_date, Appointment.appointment_time)).unique().all())


def ensure_slot_available(db: Session, doctor: Doctor, target_date: date, target_time: time, exclude_id: int | None = None) -> None:
    if not doctor.user.is_active:
        raise AppointmentValidationError("Doctor is inactive")
    if datetime.combine(target_date, target_time) <= datetime.now():
        raise AppointmentValidationError("Appointment time must be in the future")
    schedules = list(doctor.schedules)
    valid_slots = generate_available_slots(schedules, target_date)
    if target_time.strftime("%H:%M") not in valid_slots:
        raise AppointmentValidationError("Requested time is not an available doctor slot")
    statement = select(Appointment).where(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date == target_date,
        Appointment.appointment_time == target_time,
    )
    if exclude_id is not None:
        statement = statement.where(Appointment.id != exclude_id)
    if db.scalar(statement) is not None:
        raise AppointmentConflictError


def create_appointment(db: Session, patient_id: int, request: AppointmentCreateRequest) -> Appointment:
    patient = db.get(Patient, patient_id)
    if patient is None or not patient.user.is_active:
        raise AppointmentValidationError("Patient is not active")
    doctor = db.get(Doctor, request.doctor_id)
    if doctor is None:
        raise AppointmentNotFoundError
    ensure_slot_available(db, doctor, request.appointment_date, request.appointment_time)
    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor.id,
        appointment_date=request.appointment_date,
        appointment_time=request.appointment_time,
        reason=request.reason,
        status=AppointmentStatus.PENDING,
        consultation_fee=doctor.consultation_fee,
        payment_status="PENDING",
    )
    db.add(appointment)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppointmentConflictError from exc
    return get_appointment(db, appointment.id)


def transition_appointment(db: Session, appointment_id: int, target_status: AppointmentStatus) -> Appointment:
    appointment = get_appointment(db, appointment_id)
    if appointment is None:
        raise AppointmentNotFoundError
    allowed = {
        AppointmentStatus.PENDING: {AppointmentStatus.CONFIRMED, AppointmentStatus.REJECTED, AppointmentStatus.CANCELLED, AppointmentStatus.RESCHEDULED},
        AppointmentStatus.CONFIRMED: {AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED, AppointmentStatus.RESCHEDULED},
        AppointmentStatus.RESCHEDULED: {AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED},
        AppointmentStatus.REJECTED: set(),
        AppointmentStatus.COMPLETED: set(),
        AppointmentStatus.CANCELLED: set(),
    }
    if target_status not in allowed.get(AppointmentStatus(appointment.status), set()):
        raise AppointmentValidationError(f"Cannot transition appointment from {appointment.status} to {target_status}")
    appointment.status = target_status
    db.commit()
    return get_appointment(db, appointment_id)


def cancel_appointment(db: Session, appointment_id: int) -> Appointment:
    return transition_appointment(db, appointment_id, AppointmentStatus.CANCELLED)


def confirm_appointment(db: Session, appointment_id: int) -> Appointment:
    return transition_appointment(db, appointment_id, AppointmentStatus.CONFIRMED)


def reject_appointment(db: Session, appointment_id: int) -> Appointment:
    return transition_appointment(db, appointment_id, AppointmentStatus.REJECTED)


def complete_appointment(db: Session, appointment_id: int) -> Appointment:
    return transition_appointment(db, appointment_id, AppointmentStatus.COMPLETED)


def reschedule_appointment(db: Session, appointment_id: int, request: AppointmentRescheduleRequest) -> Appointment:
    appointment = get_appointment(db, appointment_id)
    if appointment is None:
        raise AppointmentNotFoundError
    if AppointmentStatus(appointment.status) not in {AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED, AppointmentStatus.RESCHEDULED}:
        raise AppointmentValidationError("Appointment cannot be rescheduled in its current state")
    doctor = db.get(Doctor, appointment.doctor_id)
    ensure_slot_available(db, doctor, request.appointment_date, request.appointment_time, appointment.id)
    appointment.appointment_date = request.appointment_date
    appointment.appointment_time = request.appointment_time
    appointment.status = AppointmentStatus.RESCHEDULED
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppointmentConflictError from exc
    return get_appointment(db, appointment_id)
