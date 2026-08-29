from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class AvailabilityStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class DoctorCreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    specialization: str = Field(min_length=1, max_length=120)
    qualification: str | None = Field(default=None, max_length=255)
    experience: int = Field(ge=0, le=100)
    department_id: int = Field(gt=0)
    consultation_fee: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    availability_status: AvailabilityStatus = AvailabilityStatus.AVAILABLE

    @field_validator("first_name", "last_name", "phone", "specialization")
    @classmethod
    def reject_blank_values(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field must not be blank")
        return normalized


class DoctorUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=30)
    specialization: str | None = Field(default=None, min_length=1, max_length=120)
    qualification: str | None = Field(default=None, max_length=255)
    experience: int | None = Field(default=None, ge=0, le=100)
    department_id: int | None = Field(default=None, gt=0)
    consultation_fee: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    availability_status: AvailabilityStatus | None = None

    @field_validator("first_name", "last_name", "phone", "specialization")
    @classmethod
    def reject_blank_values(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("This field must not be blank")
        return normalized


class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    department_id: int
    department_name: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None
    specialization: str
    qualification: str | None
    experience: int | None
    consultation_fee: Decimal
    availability_status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DoctorSummary(BaseModel):
    id: int
    user_id: int
    department_id: int
    department_name: str
    first_name: str
    last_name: str
    specialization: str
    consultation_fee: Decimal
    availability_status: str
    is_active: bool
