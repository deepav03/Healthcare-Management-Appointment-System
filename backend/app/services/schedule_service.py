from collections.abc import Iterable
from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Doctor, DoctorSchedule
from app.schemas.schedule import ScheduleRequest


class ScheduleNotFoundError(Exception):
    pass


class ScheduleConflictError(Exception):
    pass


class ScheduleValidationError(Exception):
    pass


def get_doctor_schedule(db: Session, schedule_id: int) -> DoctorSchedule | None:
    return db.get(DoctorSchedule, schedule_id)


def list_doctor_schedules(db: Session, doctor_id: int) -> list[DoctorSchedule]:
    return list(
        db.scalars(
            select(DoctorSchedule)
            .where(DoctorSchedule.doctor_id == doctor_id)
            .order_by(DoctorSchedule.day_of_week, DoctorSchedule.start_time)
        ).all()
    )


def validate_no_overlap(
    db: Session,
    doctor_id: int,
    day_of_week: int,
    start_time: time,
    end_time: time,
    schedule_id: int | None = None,
) -> None:
    existing = list(
        db.scalars(
            select(DoctorSchedule).where(
                DoctorSchedule.doctor_id == doctor_id,
                DoctorSchedule.day_of_week == day_of_week,
            )
        ).all()
    )
    for schedule in existing:
        if schedule.id == schedule_id:
            continue
        if start_time < schedule.end_time and end_time > schedule.start_time:
            raise ScheduleConflictError


def ensure_doctor(db: Session, doctor_id: int) -> Doctor:
    doctor = db.get(Doctor, doctor_id)
    if doctor is None:
        raise ScheduleNotFoundError
    return doctor


def create_schedule(db: Session, doctor_id: int, request: ScheduleRequest) -> DoctorSchedule:
    doctor = ensure_doctor(db, doctor_id)
    if not doctor.user.is_active:
        raise ScheduleValidationError("Inactive doctors cannot create schedules")
    validate_no_overlap(
        db, doctor_id, request.day_of_week, request.start_time, request.end_time
    )
    schedule = DoctorSchedule(doctor_id=doctor_id, **request.model_dump())
    db.add(schedule)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ScheduleConflictError from exc
    db.refresh(schedule)
    return schedule


def update_schedule(db: Session, schedule_id: int, request: ScheduleRequest) -> DoctorSchedule:
    schedule = get_doctor_schedule(db, schedule_id)
    if schedule is None:
        raise ScheduleNotFoundError
    validate_no_overlap(
        db,
        schedule.doctor_id,
        request.day_of_week,
        request.start_time,
        request.end_time,
        schedule_id,
    )
    for field, value in request.model_dump().items():
        setattr(schedule, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ScheduleConflictError from exc
    db.refresh(schedule)
    return schedule


def delete_schedule(db: Session, schedule_id: int) -> None:
    schedule = get_doctor_schedule(db, schedule_id)
    if schedule is None:
        raise ScheduleNotFoundError
    db.delete(schedule)
    db.commit()


def generate_available_slots(
    doctor_schedules: Iterable[DoctorSchedule],
    target_date: date,
    booked_slots: Iterable[time | str] = (),
) -> list[str]:
    """Generate slots and leave booked-slot exclusion ready for appointment integration."""
    booked = {
        datetime.strptime(slot, "%H:%M").time() if isinstance(slot, str) else slot
        for slot in booked_slots
    }
    slots: list[str] = []
    for schedule in doctor_schedules:
        if not schedule.is_available or schedule.day_of_week != target_date.weekday():
            continue
        current = datetime.combine(target_date, schedule.start_time)
        end = datetime.combine(target_date, schedule.end_time)
        break_start = schedule.break_start
        break_end = schedule.break_end
        duration = timedelta(minutes=schedule.appointment_duration)
        while current + duration <= end:
            slot_time = current.time()
            break_start_at = datetime.combine(target_date, break_start) if break_start else None
            break_end_at = datetime.combine(target_date, break_end) if break_end else None
            in_break = (
                break_start is not None
                and break_end is not None
                and current < break_end_at
                and (current + duration) > break_start_at
            )
            if not in_break and slot_time not in booked:
                slots.append(slot_time.strftime("%H:%M"))
            current += duration
    return sorted(set(slots))
