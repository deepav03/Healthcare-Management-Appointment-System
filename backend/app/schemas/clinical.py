from datetime import date, datetime

from pydantic import BaseModel, Field


class MedicalRecordCreate(BaseModel):
    patient_id: int = Field(gt=0)
    doctor_id: int = Field(gt=0)
    appointment_id: int = Field(gt=0)
    diagnosis: str | None = None
    symptoms: str | None = None
    notes: str | None = None
    treatment: str | None = None


class MedicalRecordUpdate(BaseModel):
    diagnosis: str | None = None
    symptoms: str | None = None
    notes: str | None = None
    treatment: str | None = None


class MedicalRecordResponse(MedicalRecordCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class PrescriptionItemCreate(BaseModel):
    medicine: str = Field(min_length=1, max_length=150)
    dosage: str = Field(min_length=1, max_length=100)
    frequency: str = Field(min_length=1, max_length=100)
    duration: str = Field(min_length=1, max_length=100)
    instructions: str | None = Field(default=None, max_length=500)


class PrescriptionCreate(BaseModel):
    patient_id: int = Field(gt=0)
    doctor_id: int = Field(gt=0)
    appointment_id: int = Field(gt=0)
    prescription_date: date | None = None
    items: list[PrescriptionItemCreate] = Field(min_length=1)


class PrescriptionItemResponse(PrescriptionItemCreate):
    id: int


class PrescriptionResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: int
    prescription_date: date
    created_at: datetime
    items: list[PrescriptionItemResponse]
