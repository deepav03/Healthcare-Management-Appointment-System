from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Patient, User
from app.schemas.patient import PatientUpdateRequest


class PatientNotFoundError(Exception):
    pass


class PatientConflictError(Exception):
    pass


def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.scalar(
        select(Patient)
        .options(joinedload(Patient.user))
        .where(Patient.id == patient_id)
    )


def search_patients(db: Session, query: str | None, status: str | None) -> list[Patient]:
    statement = select(Patient).options(joinedload(Patient.user)).join(Patient.user)
    if query:
        search_value = f"%{query.strip()}%"
        statement = statement.where(
            or_(
                User.first_name.ilike(search_value),
                User.last_name.ilike(search_value),
                User.email.ilike(search_value),
                User.phone.ilike(search_value),
            )
        )
    if status:
        statement = statement.where(Patient.status == status.upper())
    return list(db.scalars(statement.order_by(Patient.id)).unique().all())


def update_patient(db: Session, patient_id: int, request: PatientUpdateRequest) -> Patient:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise PatientNotFoundError

    updates = request.model_dump(exclude_unset=True)
    user_fields = {"first_name", "last_name", "email", "phone"}
    for field, value in updates.items():
        if field in user_fields:
            setattr(patient.user, field, value.lower() if field == "email" else value)
        else:
            setattr(patient, field, value.value if hasattr(value, "value") else value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise PatientConflictError from exc
    db.refresh(patient)
    return get_patient(db, patient_id)


def deactivate_patient(db: Session, patient_id: int) -> Patient:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise PatientNotFoundError
    patient.status = "INACTIVE"
    patient.user.is_active = False
    db.commit()
    db.refresh(patient)
    return get_patient(db, patient_id)
