from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_authenticated_user, require_roles
from app.db.session import get_db
from app.models import AppointmentStatus, User
from app.schemas.appointment import (
    AppointmentCreateRequest,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentRescheduleRequest,
)
from app.services.appointment_service import (
    AppointmentConflictError,
    AppointmentNotFoundError,
    AppointmentValidationError,
    cancel_appointment,
    complete_appointment,
    confirm_appointment,
    create_appointment,
    get_appointment,
    list_appointments,
    reject_appointment,
    reschedule_appointment,
)
from app.services.notification_service import create_notification

router = APIRouter(prefix="/api/appointments", tags=["appointments"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(require_authenticated_user)]


def appointment_response(appointment) -> AppointmentResponse:
    return AppointmentResponse(
        id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        patient_name=f"{appointment.patient.user.first_name} {appointment.patient.user.last_name}",
        doctor_name=f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}",
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        reason=appointment.reason,
        status=str(appointment.status),
        consultation_fee=appointment.consultation_fee,
        payment_status=str(appointment.payment_status),
        created_at=appointment.created_at,
        updated_at=appointment.updated_at,
    )


def ensure_appointment_access(appointment, current_user: User, action: str = "view") -> None:
    role = current_user.role.name.upper()
    if role == "ADMIN":
        return
    if role == "PATIENT" and appointment.patient.user_id == current_user.id:
        return
    if role == "DOCTOR" and appointment.doctor.user_id == current_user.id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Appointment {action} denied",
    )


def current_patient_id(current_user: User) -> int:
    if current_user.role.name.upper() != "PATIENT" or current_user.patient is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient access required")
    return current_user.patient.id


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(request: AppointmentCreateRequest, current_user: CurrentUser, db: DbSession):
    patient_id = current_patient_id(current_user)
    if request.patient_id is not None and request.patient_id != patient_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot book for another patient")
    try:
        appointment = create_appointment(db, patient_id, request)
        create_notification(db, appointment.doctor.user_id, "APPOINTMENT_BOOKED", "A new appointment was booked.")
        db.commit()
        return appointment_response(appointment)
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found") from exc
    except AppointmentConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Appointment slot is already booked") from exc
    except AppointmentValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/my", response_model=AppointmentListResponse)
def my_appointments(current_user: CurrentUser, db: DbSession):
    role = current_user.role.name.upper()
    appointments = list_appointments(
        db,
        patient_id=current_user.patient.id if role == "PATIENT" and current_user.patient else None,
        doctor_id=current_user.doctor.id if role == "DOCTOR" and current_user.doctor else None,
    )
    if role not in {"PATIENT", "DOCTOR"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role-specific appointment list required")
    return AppointmentListResponse(appointments=[appointment_response(item) for item in appointments], total=len(appointments))


@router.get("", response_model=AppointmentListResponse)
def all_appointments(
    current_user: Annotated[User, Depends(require_roles("ADMIN"))],
    db: DbSession,
    patient_id: Annotated[int | None, Query(gt=0)] = None,
    doctor_id: Annotated[int | None, Query(gt=0)] = None,
    appointment_date: Annotated[date | None, Query(alias="date")] = None,
    appointment_status: Annotated[str | None, Query(alias="status")] = None,
):
    appointments = list_appointments(db, patient_id, doctor_id, appointment_date, appointment_status)
    return AppointmentListResponse(appointments=[appointment_response(item) for item in appointments], total=len(appointments))


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def appointment_detail(
    appointment_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession
):
    appointment = get_appointment(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    ensure_appointment_access(appointment, current_user)
    return appointment_response(appointment)


@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
def confirm(
    appointment_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[User, Depends(require_roles("DOCTOR"))],
    db: DbSession,
):
    appointment = get_appointment(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    ensure_appointment_access(appointment, current_user, "confirmation")
    return transition(appointment_id, AppointmentStatus.CONFIRMED, db)


@router.patch("/{appointment_id}/reject", response_model=AppointmentResponse)
def reject(
    appointment_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[User, Depends(require_roles("DOCTOR"))],
    db: DbSession,
):
    appointment = get_appointment(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    ensure_appointment_access(appointment, current_user, "rejection")
    return transition(appointment_id, AppointmentStatus.REJECTED, db)


@router.patch("/{appointment_id}/complete", response_model=AppointmentResponse)
def complete(
    appointment_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[User, Depends(require_roles("DOCTOR"))],
    db: DbSession,
):
    appointment = get_appointment(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    ensure_appointment_access(appointment, current_user, "completion")
    return transition(appointment_id, AppointmentStatus.COMPLETED, db)


def transition(appointment_id: int, target: AppointmentStatus, db: Session) -> AppointmentResponse:
    try:
        if target == AppointmentStatus.CONFIRMED:
            result = confirm_appointment(db, appointment_id)
        elif target == AppointmentStatus.REJECTED:
            result = reject_appointment(db, appointment_id)
        else:
            result = complete_appointment(db, appointment_id)
        create_notification(db, result.patient.user_id, f"APPOINTMENT_{target.value}", f"Your appointment status is now {target.value}.")
        db.commit()
        return appointment_response(result)
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found") from exc
    except AppointmentValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel(
    appointment_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession
):
    appointment = get_appointment(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    ensure_appointment_access(appointment, current_user, "cancellation")
    return transition_cancel(appointment_id, db)


def transition_cancel(appointment_id: int, db: Session) -> AppointmentResponse:
    try:
        result = cancel_appointment(db, appointment_id)
        create_notification(db, result.doctor.user_id, "APPOINTMENT_CANCELLED", "An appointment was cancelled.")
        db.commit()
        return appointment_response(result)
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found") from exc
    except AppointmentValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{appointment_id}/reschedule", response_model=AppointmentResponse)
def reschedule(
    request: AppointmentRescheduleRequest,
    appointment_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[User, Depends(require_roles("PATIENT"))],
    db: DbSession,
):
    appointment = get_appointment(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    ensure_appointment_access(appointment, current_user, "rescheduling")
    try:
        result = reschedule_appointment(db, appointment_id, request)
        create_notification(db, result.doctor.user_id, "APPOINTMENT_RESCHEDULED", "An appointment was rescheduled.")
        db.commit()
        return appointment_response(result)
    except AppointmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found") from exc
    except AppointmentConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Appointment slot is already booked") from exc
    except AppointmentValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
