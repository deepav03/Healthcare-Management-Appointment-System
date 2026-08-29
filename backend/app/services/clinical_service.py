from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Appointment, AppointmentStatus, Doctor, MedicalRecord, Patient, Prescription, PrescriptionItem
from app.schemas.clinical import MedicalRecordCreate, MedicalRecordUpdate, PrescriptionCreate


class ClinicalNotFoundError(Exception):
    pass


class ClinicalConflictError(Exception):
    pass


class ClinicalValidationError(Exception):
    pass


def record_query():
    return select(MedicalRecord).options(joinedload(MedicalRecord.appointment))


def prescription_query():
    return select(Prescription).options(joinedload(Prescription.items))


def get_record(db: Session, record_id: int):
    return db.scalar(record_query().where(MedicalRecord.id == record_id))


def list_records(db: Session, patient_id: int | None = None, doctor_id: int | None = None):
    statement = record_query()
    if patient_id is not None:
        statement = statement.where(MedicalRecord.patient_id == patient_id)
    if doctor_id is not None:
        statement = statement.where(MedicalRecord.doctor_id == doctor_id)
    return list(db.scalars(statement.order_by(MedicalRecord.created_at.desc())).unique().all())


def create_record(db: Session, request: MedicalRecordCreate):
    appointment = db.get(Appointment, request.appointment_id)
    if appointment is None or appointment.patient_id != request.patient_id or appointment.doctor_id != request.doctor_id:
        raise ClinicalValidationError("Appointment does not match patient and doctor")
    if AppointmentStatus(appointment.status) != AppointmentStatus.COMPLETED:
        raise ClinicalValidationError("Medical records require a completed appointment")
    if db.scalar(select(MedicalRecord).where(MedicalRecord.appointment_id == request.appointment_id)):
        raise ClinicalConflictError
    record = MedicalRecord(**request.model_dump())
    db.add(record)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ClinicalConflictError from exc
    return get_record(db, record.id)


def update_record(db: Session, record_id: int, request: MedicalRecordUpdate):
    record = get_record(db, record_id)
    if record is None:
        raise ClinicalNotFoundError
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    return get_record(db, record_id)


def get_prescription(db: Session, prescription_id: int):
    return db.scalar(prescription_query().where(Prescription.id == prescription_id))


def list_prescriptions(db: Session, patient_id: int | None = None, doctor_id: int | None = None):
    statement = prescription_query()
    if patient_id is not None:
        statement = statement.where(Prescription.patient_id == patient_id)
    if doctor_id is not None:
        statement = statement.where(Prescription.doctor_id == doctor_id)
    return list(db.scalars(statement.order_by(Prescription.created_at.desc())).unique().all())


def create_prescription(db: Session, request: PrescriptionCreate):
    appointment = db.get(Appointment, request.appointment_id)
    if appointment is None or appointment.patient_id != request.patient_id or appointment.doctor_id != request.doctor_id:
        raise ClinicalValidationError("Appointment does not match patient and doctor")
    if AppointmentStatus(appointment.status) != AppointmentStatus.COMPLETED:
        raise ClinicalValidationError("Prescriptions require a completed appointment")
    if db.scalar(select(Prescription).where(Prescription.appointment_id == request.appointment_id)):
        raise ClinicalConflictError
    prescription = Prescription(
        patient_id=request.patient_id,
        doctor_id=request.doctor_id,
        appointment_id=request.appointment_id,
        prescription_date=request.prescription_date,
        items=[PrescriptionItem(**item.model_dump()) for item in request.items],
    )
    db.add(prescription)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ClinicalConflictError from exc
    return get_prescription(db, prescription.id)
