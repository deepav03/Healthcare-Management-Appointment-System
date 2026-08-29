from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_authenticated_user, require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.clinical import (
    MedicalRecordCreate,
    MedicalRecordResponse,
    MedicalRecordUpdate,
    PrescriptionCreate,
    PrescriptionResponse,
)
from app.services.clinical_service import (
    ClinicalConflictError,
    ClinicalNotFoundError,
    ClinicalValidationError,
    create_prescription,
    create_record,
    get_prescription,
    get_record,
    list_prescriptions,
    list_records,
    update_record,
)
from app.services.notification_service import create_notification

router = APIRouter(tags=["clinical"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(require_authenticated_user)]


def record_response(record):
    return MedicalRecordResponse.model_validate(record, from_attributes=True)


def prescription_response(prescription):
    return PrescriptionResponse.model_validate(prescription, from_attributes=True)


def can_access_patient(current_user: User, patient_id: int, action: str = "view"):
    role = current_user.role.name.upper()
    if role == "PATIENT" and (current_user.patient is None or current_user.patient.id != patient_id):
        raise HTTPException(status_code=403, detail=f"Medical data {action} denied")


def can_access_doctor(current_user: User, doctor_id: int, action: str = "view"):
    if current_user.role.name.upper() == "DOCTOR" and (current_user.doctor is None or current_user.doctor.id != doctor_id):
        raise HTTPException(status_code=403, detail=f"Medical data {action} denied")


@router.post("/api/medical-records", response_model=MedicalRecordResponse, status_code=201)
def add_record(request: MedicalRecordCreate, current_user: Annotated[User, Depends(require_roles("DOCTOR", "ADMIN"))], db: DbSession):
    if current_user.role.name.upper() == "DOCTOR":
        if current_user.doctor is None or request.doctor_id != current_user.doctor.id:
            raise HTTPException(status_code=403, detail="Medical record creation denied")
    try:
        record = create_record(db, request)
        create_notification(db, record.patient.user_id if record.patient else request.patient_id, "MEDICAL_RECORD_CREATED", "A medical record was created.")
        db.commit()
        return record_response(record)
    except ClinicalConflictError as exc:
        raise HTTPException(status_code=409, detail="A medical record already exists for this appointment") from exc
    except ClinicalValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/medical-records", response_model=list[MedicalRecordResponse])
def records(current_user: CurrentUser, db: DbSession):
    role = current_user.role.name.upper()
    if role == "PATIENT":
        result = list_records(db, patient_id=current_user.patient.id if current_user.patient else 0)
    elif role == "DOCTOR":
        result = list_records(db, doctor_id=current_user.doctor.id if current_user.doctor else 0)
    else:
        result = list_records(db)
    return [record_response(item) for item in result]


@router.get("/api/medical-records/{record_id}", response_model=MedicalRecordResponse)
def record_detail(record_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    record = get_record(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Medical record not found")
    can_access_patient(current_user, record.patient_id)
    can_access_doctor(current_user, record.doctor_id)
    return record_response(record)


@router.get("/api/patients/{patient_id}/medical-records", response_model=list[MedicalRecordResponse])
def patient_records(patient_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    can_access_patient(current_user, patient_id)
    if current_user.role.name.upper() not in {"PATIENT", "DOCTOR", "ADMIN"}:
        raise HTTPException(status_code=403, detail="Medical record access denied")
    return [record_response(item) for item in list_records(db, patient_id=patient_id)]


@router.patch("/api/medical-records/{record_id}", response_model=MedicalRecordResponse)
def edit_record(record_id: Annotated[int, Path(ge=1)], request: MedicalRecordUpdate, current_user: Annotated[User, Depends(require_roles("DOCTOR", "ADMIN"))], db: DbSession):
    record = get_record(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Medical record not found")
    can_access_doctor(current_user, record.doctor_id, "update")
    try:
        return record_response(update_record(db, record_id, request))
    except ClinicalNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Medical record not found") from exc


@router.post("/api/prescriptions", response_model=PrescriptionResponse, status_code=201)
def add_prescription(request: PrescriptionCreate, current_user: Annotated[User, Depends(require_roles("DOCTOR", "ADMIN"))], db: DbSession):
    if current_user.role.name.upper() == "DOCTOR" and (current_user.doctor is None or request.doctor_id != current_user.doctor.id):
        raise HTTPException(status_code=403, detail="Prescription creation denied")
    try:
        prescription = create_prescription(db, request)
        create_notification(db, prescription.patient.user_id if prescription.patient else request.patient_id, "PRESCRIPTION_CREATED", "A prescription was created.")
        db.commit()
        return prescription_response(prescription)
    except ClinicalConflictError as exc:
        raise HTTPException(status_code=409, detail="A prescription already exists for this appointment") from exc
    except ClinicalValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/prescriptions", response_model=list[PrescriptionResponse])
def prescriptions(current_user: CurrentUser, db: DbSession):
    role = current_user.role.name.upper()
    if role == "PATIENT":
        result = list_prescriptions(db, patient_id=current_user.patient.id if current_user.patient else 0)
    elif role == "DOCTOR":
        result = list_prescriptions(db, doctor_id=current_user.doctor.id if current_user.doctor else 0)
    elif role == "ADMIN":
        result = list_prescriptions(db)
    else:
        raise HTTPException(status_code=403, detail="Prescription access denied")
    return [prescription_response(item) for item in result]


@router.get("/api/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
def prescription_detail(prescription_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    prescription = get_prescription(db, prescription_id)
    if prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    can_access_patient(current_user, prescription.patient_id)
    can_access_doctor(current_user, prescription.doctor_id)
    return prescription_response(prescription)


@router.get("/api/patients/{patient_id}/prescriptions", response_model=list[PrescriptionResponse])
def patient_prescriptions(patient_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    can_access_patient(current_user, patient_id)
    return [prescription_response(item) for item in list_prescriptions(db, patient_id=patient_id)]
