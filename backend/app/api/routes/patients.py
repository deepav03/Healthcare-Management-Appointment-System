from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_authenticated_user, require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.patient import PatientResponse, PatientSummary, PatientUpdateRequest
from app.services.patient_service import (
    PatientConflictError,
    PatientNotFoundError,
    deactivate_patient,
    get_patient,
    search_patients,
    update_patient,
)

router = APIRouter(prefix="/api/patients", tags=["patients"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(require_authenticated_user)]
AdminOrDoctor = Annotated[User, Depends(require_roles("ADMIN", "DOCTOR"))]


def to_patient_response(patient) -> PatientResponse:
    return PatientResponse(
        id=patient.id,
        user_id=patient.user_id,
        email=patient.user.email,
        first_name=patient.user.first_name,
        last_name=patient.user.last_name,
        phone=patient.user.phone,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        address=patient.address,
        emergency_contact=patient.emergency_contact,
        blood_group=patient.blood_group,
        status=patient.status,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
    )


def ensure_patient_access(patient_id: int, current_user: User, patient) -> None:
    if current_user.role.name.upper() == "PATIENT" and (
        patient is None or patient.user_id != current_user.id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient access denied")


@router.get("/me", response_model=PatientResponse)
def my_patient_profile(current_user: CurrentUser, db: DbSession):
    if current_user.role.name.upper() != "PATIENT":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patient profile access required")
    patient = get_patient(db, current_user.patient.id if current_user.patient else 0)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return to_patient_response(patient)


@router.get("", response_model=list[PatientSummary])
def list_patients(
    current_user: AdminOrDoctor,
    db: DbSession,
    query: Annotated[str | None, Query(max_length=100)] = None,
    patient_status: Annotated[str | None, Query(alias="status", max_length=30)] = None,
):
    patients = search_patients(db, query, patient_status)
    return [
        PatientSummary(
            id=patient.id,
            user_id=patient.user_id,
            email=patient.user.email,
            first_name=patient.user.first_name,
            last_name=patient.user.last_name,
            phone=patient.user.phone,
            status=patient.status,
        )
        for patient in patients
    ]


@router.get("/{patient_id}", response_model=PatientResponse)
def patient_detail(
    patient_id: Annotated[int, Path(ge=1)],
    current_user: CurrentUser,
    db: DbSession,
):
    patient = get_patient(db, patient_id)
    ensure_patient_access(patient_id, current_user, patient)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return to_patient_response(patient)


@router.patch("/{patient_id}", response_model=PatientResponse)
def edit_patient(
    request: PatientUpdateRequest,
    patient_id: Annotated[int, Path(ge=1)],
    current_user: CurrentUser,
    db: DbSession,
):
    patient = get_patient(db, patient_id)
    ensure_patient_access(patient_id, current_user, patient)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    try:
        return to_patient_response(update_patient(db, patient_id, request))
    except PatientConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or phone is already registered") from exc


@router.post("/{patient_id}/deactivate", response_model=PatientResponse)
def deactivate_patient_account(
    patient_id: Annotated[int, Path(ge=1)],
    current_user: Annotated[User, Depends(require_roles("ADMIN"))],
    db: DbSession,
):
    try:
        return to_patient_response(deactivate_patient(db, patient_id))
    except PatientNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found") from exc
