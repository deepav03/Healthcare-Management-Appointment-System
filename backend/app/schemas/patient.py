from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


class BloodGroup(StrEnum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class PatientUpdateRequest(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=30)
    date_of_birth: date | None = None
    gender: Gender | None = None
    address: str | None = Field(default=None, max_length=500)
    emergency_contact: str | None = Field(default=None, max_length=255)
    blood_group: BloodGroup | None = None

    @field_validator("first_name", "last_name", "phone", mode="before")
    @classmethod
    def reject_blank_values(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("This field must not be blank")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def date_of_birth_cannot_be_in_future(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None
    date_of_birth: date | None
    gender: str | None
    address: str | None
    emergency_contact: str | None
    blood_group: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class PatientSummary(BaseModel):
    id: int
    user_id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None
    status: str
