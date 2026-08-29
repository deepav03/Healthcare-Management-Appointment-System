from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Appointment, Bill, Payment, PaymentStatus
from app.schemas.billing import BillCreate, PaymentCreate


class BillingNotFoundError(Exception):
    pass


class BillingConflictError(Exception):
    pass


class BillingValidationError(Exception):
    pass


def get_bill(db: Session, bill_id: int):
    return db.get(Bill, bill_id)


def list_bills(db: Session, patient_id: int | None = None):
    statement = select(Bill).order_by(Bill.created_at.desc())
    if patient_id is not None:
        statement = statement.where(Bill.patient_id == patient_id)
    return list(db.scalars(statement).all())


def create_bill(db: Session, request: BillCreate):
    appointment = db.get(Appointment, request.appointment_id)
    if appointment is None:
        raise BillingNotFoundError
    if appointment.patient_id != request.patient_id:
        raise BillingValidationError("Bill patient does not match appointment patient")
    if db.scalar(select(Bill).where(Bill.appointment_id == request.appointment_id)):
        raise BillingConflictError
    consultation_fee = Decimal(appointment.consultation_fee)
    subtotal = consultation_fee + request.additional_charges - request.discount
    if subtotal < 0:
        raise BillingValidationError("Discount cannot exceed bill charges")
    total = subtotal + request.tax
    bill = Bill(
        patient_id=request.patient_id,
        appointment_id=request.appointment_id,
        consultation_fee=consultation_fee,
        additional_charges=request.additional_charges,
        discount=request.discount,
        tax=request.tax,
        total_amount=total,
        payment_status=PaymentStatus.PENDING,
    )
    db.add(bill)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise BillingConflictError from exc
    db.refresh(bill)
    return bill


def create_payment(db: Session, patient_id: int, request: PaymentCreate):
    bill = db.get(Bill, request.bill_id)
    if bill is None:
        raise BillingNotFoundError
    if bill.patient_id != patient_id:
        raise BillingValidationError("Payment does not belong to this patient")
    if bill.payment_status == PaymentStatus.SUCCESS:
        raise BillingConflictError
    if Decimal(request.amount) != Decimal(bill.total_amount):
        raise BillingValidationError("Payment amount must equal the bill total")
    outcome = request.outcome
    if outcome not in {PaymentStatus.SUCCESS, PaymentStatus.FAILED}:
        raise BillingValidationError("Payment outcome must be SUCCESS or FAILED")
    payment = Payment(
        bill_id=bill.id,
        patient_id=patient_id,
        amount=request.amount,
        payment_method=request.payment_method.value,
        transaction_id=f"SIM-{uuid4().hex[:20].upper()}",
        payment_status=outcome,
        payment_date=datetime.now(UTC),
    )
    if outcome == PaymentStatus.SUCCESS:
        bill.payment_status = PaymentStatus.SUCCESS
    db.add(payment)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise BillingConflictError from exc
    db.refresh(payment)
    return payment


def get_payment(db: Session, payment_id: int):
    return db.get(Payment, payment_id)


def list_payments(db: Session, patient_id: int | None = None, bill_id: int | None = None):
    statement = select(Payment).order_by(Payment.created_at.desc())
    if patient_id is not None:
        statement = statement.where(Payment.patient_id == patient_id)
    if bill_id is not None:
        statement = statement.where(Payment.bill_id == bill_id)
    return list(db.scalars(statement).all())
