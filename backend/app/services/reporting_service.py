from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Appointment, Bill, Doctor, MedicalRecord, Notification, Patient, Payment, PaymentStatus, Prescription, User


def admin_dashboard(db: Session) -> dict:
    today = date.today()
    count = lambda statement: db.scalar(statement) or 0
    return {
        "total_patients": count(select(func.count(Patient.id))),
        "total_doctors": count(select(func.count(Doctor.id))),
        "today_appointments": count(select(func.count(Appointment.id)).where(Appointment.appointment_date == today)),
        "pending_appointments": count(select(func.count(Appointment.id)).where(Appointment.status == "PENDING")),
        "confirmed_appointments": count(select(func.count(Appointment.id)).where(Appointment.status == "CONFIRMED")),
        "completed_appointments": count(select(func.count(Appointment.id)).where(Appointment.status == "COMPLETED")),
        "cancelled_appointments": count(select(func.count(Appointment.id)).where(Appointment.status == "CANCELLED")),
        "total_revenue": db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.payment_status == PaymentStatus.SUCCESS)) or 0,
        "successful_payments": count(select(func.count(Payment.id)).where(Payment.payment_status == PaymentStatus.SUCCESS)),
        "failed_payments": count(select(func.count(Payment.id)).where(Payment.payment_status == PaymentStatus.FAILED)),
    }


def doctor_dashboard(db: Session, doctor_id: int) -> dict:
    today = date.today()
    count = lambda statement: db.scalar(statement) or 0
    return {
        "today_appointments": count(select(func.count(Appointment.id)).where(Appointment.doctor_id == doctor_id, Appointment.appointment_date == today)),
        "upcoming_appointments": count(select(func.count(Appointment.id)).where(Appointment.doctor_id == doctor_id, Appointment.appointment_date >= today)),
        "completed_appointments": count(select(func.count(Appointment.id)).where(Appointment.doctor_id == doctor_id, Appointment.status == "COMPLETED")),
        "patient_count": count(select(func.count(func.distinct(Appointment.patient_id))).where(Appointment.doctor_id == doctor_id)),
    }


def patient_dashboard(db: Session, patient_id: int, user_id: int) -> dict:
    today = date.today()
    count = lambda statement: db.scalar(statement) or 0
    return {
        "upcoming_appointment": db.scalar(select(Appointment.id).where(Appointment.patient_id == patient_id, Appointment.appointment_date >= today, Appointment.status.in_(["PENDING", "CONFIRMED", "RESCHEDULED"])).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(1)),
        "appointment_count": count(select(func.count(Appointment.id)).where(Appointment.patient_id == patient_id)),
        "medical_record_count": count(select(func.count(MedicalRecord.id)).where(MedicalRecord.patient_id == patient_id)),
        "prescription_count": count(select(func.count(Prescription.id)).where(Prescription.patient_id == patient_id)),
        "pending_bill_count": count(select(func.count(Bill.id)).where(Bill.patient_id == patient_id, Bill.payment_status == PaymentStatus.PENDING)),
        "unread_notification_count": count(select(func.count(Notification.id)).where(Notification.user_id == user_id, Notification.read_status.is_(False))),
    }


def appointment_report(db: Session, start_date: date | None, end_date: date | None, doctor_id: int | None, appointment_status: str | None):
    statement = select(Appointment)
    if start_date: statement = statement.where(Appointment.appointment_date >= start_date)
    if end_date: statement = statement.where(Appointment.appointment_date <= end_date)
    if doctor_id: statement = statement.where(Appointment.doctor_id == doctor_id)
    if appointment_status: statement = statement.where(Appointment.status == appointment_status.upper())
    return [{"id": item.id, "doctor_id": item.doctor_id, "patient_id": item.patient_id, "date": item.appointment_date, "status": str(item.status)} for item in db.scalars(statement.order_by(Appointment.appointment_date)).all()]


def revenue_report(db: Session, start_date: date | None, end_date: date | None):
    statement = select(Bill)
    if start_date: statement = statement.where(Bill.invoice_date >= start_date)
    if end_date: statement = statement.where(Bill.invoice_date <= end_date)
    return [{"id": item.id, "patient_id": item.patient_id, "total_amount": item.total_amount, "payment_status": str(item.payment_status), "invoice_date": item.invoice_date} for item in db.scalars(statement.order_by(Bill.invoice_date)).all()]


def payment_report(db: Session, start_date: date | None, end_date: date | None):
    statement = select(Payment)
    if start_date: statement = statement.where(func.date(Payment.created_at) >= start_date)
    if end_date: statement = statement.where(func.date(Payment.created_at) <= end_date)
    return [{"id": item.id, "bill_id": item.bill_id, "amount": item.amount, "status": str(item.payment_status), "payment_method": item.payment_method} for item in db.scalars(statement.order_by(Payment.created_at)).all()]


def patient_report(db: Session):
    return [{"id": item.id, "user_id": item.user_id, "status": item.status} for item in db.scalars(select(Patient).order_by(Patient.id)).all()]
