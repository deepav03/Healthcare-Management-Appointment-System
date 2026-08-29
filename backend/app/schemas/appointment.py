from datetime import date, time, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator


class AppointmentStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"


class AppointmentCreateRequest(BaseModel):
    doctor_id: int = Field(gt=0)
    appointment_date: date
    appointment_time: time
    reason: str | None = Field(default=None, max_length=500)
    patient_id: int | None = Field(default=None, gt=0)

    @field_validator("appointment_date")
    @classmethod
    def date_must_not_be_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Appointment date cannot be in the past")
        return value

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class AppointmentRescheduleRequest(BaseModel):
    appointment_date: date
    appointment_time: time

    @field_validator("appointment_date")
    @classmethod
    def date_must_not_be_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Appointment date cannot be in the past")
        return value


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    patient_name: str
    doctor_name: str
    appointment_date: date
    appointment_time: time
    reason: str | None
    status: str
    consultation_fee: Decimal
    payment_status: str
    created_at: datetime
    updated_at: datetime


class AppointmentListResponse(BaseModel):
    appointments: list[AppointmentResponse]
    total: int
