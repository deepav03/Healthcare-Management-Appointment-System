from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.api.dependencies import require_authenticated_user, require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.billing import BillCreate, BillResponse, PaymentCreate, PaymentResponse
from app.services.billing_service import (
    BillingConflictError,
    BillingNotFoundError,
    BillingValidationError,
    create_bill,
    create_payment,
    get_bill,
    get_payment,
    list_bills,
    list_payments,
)
from app.services.notification_service import create_notification

router = APIRouter(tags=["billing"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(require_authenticated_user)]


def bill_response(bill):
    return BillResponse.model_validate(bill, from_attributes=True)


def payment_response(payment):
    return PaymentResponse.model_validate(payment, from_attributes=True)


def patient_id_for(user: User) -> int:
    if user.patient is None:
        raise HTTPException(status_code=403, detail="Patient access required")
    return user.patient.id


def visible_bill(bill, user: User):
    if user.role.name.upper() != "ADMIN" and bill.patient_id != patient_id_for(user):
        raise HTTPException(status_code=403, detail="Bill access denied")


@router.post("/api/bills", response_model=BillResponse, status_code=201)
def add_bill(request: BillCreate, current_user: Annotated[User, Depends(require_roles("ADMIN", "DOCTOR"))], db: DbSession):
    try:
        bill = create_bill(db, request)
        create_notification(db, bill.patient.user_id if bill.patient else request.patient_id, "BILL_GENERATED", "A bill was generated.")
        db.commit()
        return bill_response(bill)
    except BillingNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Appointment not found") from exc
    except BillingConflictError as exc:
        raise HTTPException(status_code=409, detail="A bill already exists for this appointment") from exc
    except BillingValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/bills", response_model=list[BillResponse])
def bills(current_user: CurrentUser, db: DbSession):
    if current_user.role.name.upper() == "PATIENT":
        result = list_bills(db, patient_id=patient_id_for(current_user))
    elif current_user.role.name.upper() == "ADMIN":
        result = list_bills(db)
    else:
        result = []
    return [bill_response(item) for item in result]


@router.get("/api/bills/{bill_id}", response_model=BillResponse)
def bill_detail(bill_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    bill = get_bill(db, bill_id)
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    visible_bill(bill, current_user)
    return bill_response(bill)


@router.get("/api/patients/{patient_id}/bills", response_model=list[BillResponse])
def patient_bills(patient_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    if current_user.role.name.upper() != "ADMIN" and patient_id != patient_id_for(current_user):
        raise HTTPException(status_code=403, detail="Bill access denied")
    return [bill_response(item) for item in list_bills(db, patient_id)]


@router.post("/api/payments", response_model=PaymentResponse, status_code=201)
def add_payment(request: PaymentCreate, current_user: Annotated[User, Depends(require_roles("PATIENT"))], db: DbSession):
    try:
        payment = create_payment(db, patient_id_for(current_user), request)
        create_notification(db, current_user.id, f"PAYMENT_{payment.payment_status}", f"Payment {payment.payment_status.lower()}.")
        db.commit()
        return payment_response(payment)
    except BillingNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Bill not found") from exc
    except BillingConflictError as exc:
        raise HTTPException(status_code=409, detail="Bill has already been paid") from exc
    except BillingValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/payments", response_model=list[PaymentResponse])
def payments(current_user: CurrentUser, db: DbSession):
    if current_user.role.name.upper() == "PATIENT":
        result = list_payments(db, patient_id=patient_id_for(current_user))
    elif current_user.role.name.upper() == "ADMIN":
        result = list_payments(db)
    else:
        result = []
    return [payment_response(item) for item in result]


@router.get("/api/payments/{payment_id}", response_model=PaymentResponse)
def payment_detail(payment_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    payment = get_payment(db, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    if current_user.role.name.upper() != "ADMIN" and payment.patient_id != patient_id_for(current_user):
        raise HTTPException(status_code=403, detail="Payment access denied")
    return payment_response(payment)


@router.get("/api/bills/{bill_id}/payments", response_model=list[PaymentResponse])
def bill_payments(bill_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    bill = get_bill(db, bill_id)
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    visible_bill(bill, current_user)
    return [payment_response(item) for item in list_payments(db, bill_id=bill_id)]
