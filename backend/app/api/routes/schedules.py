from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_authenticated_user
from app.db.session import get_db
from app.models import Doctor, DoctorSchedule, User
from app.schemas.schedule import AvailabilityResponse, ScheduleRequest, ScheduleResponse, WeeklyAvailabilityResponse
from app.services.doctor_service import get_doctor
from app.services.schedule_service import (
    ScheduleConflictError,
    ScheduleNotFoundError,
    ScheduleValidationError,
    create_schedule,
    delete_schedule,
    generate_available_slots,
    get_doctor_schedule,
    list_doctor_schedules,
    update_schedule,
)

router = APIRouter(tags=["doctor schedules"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(require_authenticated_user)]


def schedule_response(schedule: DoctorSchedule) -> ScheduleResponse:
    return ScheduleResponse(
        id=schedule.id,
        doctor_id=schedule.doctor_id,
        day_of_week=schedule.day_of_week,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
        appointment_duration=schedule.appointment_duration,
        break_start=schedule.break_start,
        break_end=schedule.break_end,
        is_available=schedule.is_available,
    )


def doctor_for_schedule_access(
    db: Session, doctor_id: int, current_user: User, modify: bool = False
) -> Doctor:
    doctor = get_doctor(db, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    role = current_user.role.name.upper()
    if modify:
        if role == "PATIENT":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Schedule modification denied")
        if role == "DOCTOR" and doctor.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Schedule access denied")
    elif role == "DOCTOR" and doctor.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Schedule access denied")
    elif role == "PATIENT" and not doctor.user.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doctor


def schedule_for_update_access(db: Session, schedule_id: int, current_user: User) -> DoctorSchedule:
    schedule = get_doctor_schedule(db, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    doctor_for_schedule_access(db, schedule.doctor_id, current_user, modify=True)
    return schedule


@router.get("/api/doctors/{doctor_id}/schedules", response_model=list[ScheduleResponse])
def get_schedules(doctor_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    doctor_for_schedule_access(db, doctor_id, current_user)
    return [schedule_response(item) for item in list_doctor_schedules(db, doctor_id)]


@router.post("/api/doctors/{doctor_id}/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
def add_schedule(
    doctor_id: Annotated[int, Path(ge=1)], request: ScheduleRequest, current_user: CurrentUser, db: DbSession
):
    doctor_for_schedule_access(db, doctor_id, current_user, modify=True)
    try:
        return schedule_response(create_schedule(db, doctor_id, request))
    except ScheduleConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Schedule overlaps an existing schedule") from exc
    except ScheduleValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/api/schedules/{schedule_id}", response_model=ScheduleResponse)
def edit_schedule(
    schedule_id: Annotated[int, Path(ge=1)], request: ScheduleRequest, current_user: CurrentUser, db: DbSession
):
    schedule_for_update_access(db, schedule_id, current_user)
    try:
        return schedule_response(update_schedule(db, schedule_id, request))
    except ScheduleConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Schedule overlaps an existing schedule") from exc


@router.delete("/api/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_schedule(schedule_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    schedule_for_update_access(db, schedule_id, current_user)
    delete_schedule(db, schedule_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/api/doctors/{doctor_id}/availability", response_model=WeeklyAvailabilityResponse)
def get_availability(doctor_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    doctor = doctor_for_schedule_access(db, doctor_id, current_user)
    schedules = [schedule_response(item) for item in list_doctor_schedules(db, doctor_id)]
    return WeeklyAvailabilityResponse(doctor_id=doctor_id, is_active=doctor.user.is_active, schedules=schedules)


@router.get("/api/doctors/{doctor_id}/availability/{availability_date}", response_model=AvailabilityResponse)
def get_daily_availability(
    doctor_id: Annotated[int, Path(ge=1)],
    availability_date: date,
    current_user: CurrentUser,
    db: DbSession,
):
    doctor = doctor_for_schedule_access(db, doctor_id, current_user)
    if availability_date < date.today():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Availability date cannot be in the past")
    slots = generate_available_slots(list_doctor_schedules(db, doctor_id), availability_date)
    return AvailabilityResponse(doctor_id=doctor.id, date=availability_date, available_slots=slots)
