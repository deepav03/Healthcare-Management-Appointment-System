from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class PaymentMethod(StrEnum):
    UPI = "UPI"
    CARD = "CARD"
    CASH = "CASH"


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class BillCreate(BaseModel):
    patient_id: int = Field(gt=0)
    appointment_id: int = Field(gt=0)
    additional_charges: Decimal = Field(default=0, ge=0, decimal_places=2)
    discount: Decimal = Field(default=0, ge=0, decimal_places=2)
    tax: Decimal = Field(default=0, ge=0, decimal_places=2)


class BillResponse(BaseModel):
    id: int
    patient_id: int
    appointment_id: int
    consultation_fee: Decimal
    additional_charges: Decimal
    discount: Decimal
    tax: Decimal
    total_amount: Decimal
    payment_status: str
    invoice_date: date
    created_at: datetime


class PaymentCreate(BaseModel):
    bill_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, decimal_places=2)
    payment_method: PaymentMethod
    outcome: PaymentStatus = PaymentStatus.SUCCESS


class PaymentResponse(BaseModel):
    id: int
    bill_id: int
    patient_id: int
    amount: Decimal
    payment_method: str
    transaction_id: str | None
    payment_status: str
    payment_date: datetime | None
    created_at: datetime
