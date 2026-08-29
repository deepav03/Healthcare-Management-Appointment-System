from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_authenticated_user, require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.doctor import (
    DoctorCreateRequest,
    DoctorResponse,
    DoctorSummary,
    DoctorUpdateRequest,
)
from app.services.doctor_service import (
    DepartmentNotFoundError,
    DoctorConflictError,
    DoctorNotFoundError,
    create_doctor,
    get_doctor,
    list_doctors,
    set_doctor_active,
    update_doctor,
)

router = APIRouter(prefix="/api/doctors", tags=["doctors"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(require_authenticated_user)]
AdminUser = Annotated[User, Depends(require_roles("ADMIN"))]


def doctor_response(doctor) -> DoctorResponse:
    return DoctorResponse(
        id=doctor.id,
        user_id=doctor.user_id,
        department_id=doctor.department_id,
        department_name=doctor.department.name,
        first_name=doctor.user.first_name,
        last_name=doctor.user.last_name,
        email=doctor.user.email,
        phone=doctor.user.phone,
        specialization=doctor.specialization,
        qualification=doctor.qualification,
        experience=doctor.experience,
        consultation_fee=doctor.consultation_fee,
        availability_status=doctor.availability_status,
        is_active=doctor.user.is_active,
        created_at=doctor.created_at,
        updated_at=doctor.updated_at,
    )


def doctor_summary(doctor) -> DoctorSummary:
    return DoctorSummary(
        id=doctor.id,
        user_id=doctor.user_id,
        department_id=doctor.department_id,
        department_name=doctor.department.name,
        first_name=doctor.user.first_name,
        last_name=doctor.user.last_name,
        specialization=doctor.specialization,
        consultation_fee=doctor.consultation_fee,
        availability_status=doctor.availability_status,
        is_active=doctor.user.is_active,
    )


def visible_to_user(doctor, current_user: User) -> bool:
    role = current_user.role.name.upper()
    return role == "ADMIN" or doctor.user_id == current_user.id or doctor.user.is_active


@router.post("", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor_endpoint(request: DoctorCreateRequest, current_user: AdminUser, db: DbSession):
    try:
        return doctor_response(create_doctor(db, request))
    except DepartmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found") from exc
    except DoctorConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Doctor email or phone is already registered") from exc


@router.get("", response_model=list[DoctorSummary])
def list_doctors_endpoint(
    current_user: CurrentUser,
    db: DbSession,
    search: Annotated[str | None, Query(max_length=100)] = None,
    specialization: Annotated[str | None, Query(max_length=120)] = None,
    department: Annotated[int | None, Query(gt=0)] = None,
    active: bool | None = None,
):
    role = current_user.role.name.upper()
    if role == "PATIENT" or (role == "DOCTOR" and active is None):
        active = True
    return [doctor_summary(doctor) for doctor in list_doctors(db, search, specialization, department, active)]


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor_endpoint(
    doctor_id: Annotated[int, Path(ge=1)],
    current_user: CurrentUser,
    db: DbSession,
):
    doctor = get_doctor(db, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    if not visible_to_user(doctor, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doctor_response(doctor)


@router.patch("/{doctor_id}", response_model=DoctorResponse)
def update_doctor_endpoint(
    request: DoctorUpdateRequest,
    doctor_id: Annotated[int, Path(ge=1)],
    current_user: CurrentUser,
    db: DbSession,
):
    doctor = get_doctor(db, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    if current_user.role.name.upper() != "ADMIN" and doctor.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor profile access denied")
    if current_user.role.name.upper() == "PATIENT":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor profile modification denied")
    try:
        return doctor_response(update_doctor(db, doctor_id, request))
    except DepartmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found") from exc
    except DoctorConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Doctor email or phone is already registered") from exc


@router.post("/{doctor_id}/activate", response_model=DoctorResponse)
def activate_doctor_endpoint(
    doctor_id: Annotated[int, Path(ge=1)], current_user: AdminUser, db: DbSession
):
    try:
        return doctor_response(set_doctor_active(db, doctor_id, True))
    except DoctorNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found") from exc


@router.post("/{doctor_id}/deactivate", response_model=DoctorResponse)
def deactivate_doctor_endpoint(
    doctor_id: Annotated[int, Path(ge=1)], current_user: AdminUser, db: DbSession
):
    try:
        return doctor_response(set_doctor_active(db, doctor_id, False))
    except DoctorNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found") from exc
