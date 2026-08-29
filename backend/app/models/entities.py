from datetime import date, datetime, time
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class AppointmentStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255))

    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_name", "last_name", "first_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    role: Mapped["Role"] = relationship(back_populates="users")
    patient: Mapped["Patient | None"] = relationship(back_populates="user", uselist=False)
    doctor: Mapped["Doctor | None"] = relationship(back_populates="user", uselist=False)
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), unique=True, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    gender: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(String(500))
    emergency_contact: Mapped[str | None] = mapped_column(String(255))
    blood_group: Mapped[str | None] = mapped_column(String(5))
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE", server_default="ACTIVE", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="patient")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient")
    medical_records: Mapped[list["MedicalRecord"]] = relationship(back_populates="patient")
    prescriptions: Mapped[list["Prescription"]] = relationship(back_populates="patient")
    bills: Mapped[list["Bill"]] = relationship(back_populates="patient")
    payments: Mapped[list["Payment"]] = relationship(back_populates="patient")


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")

    doctors: Mapped[list["Doctor"]] = relationship(back_populates="department")


class Doctor(Base):
    __tablename__ = "doctors"
    __table_args__ = (Index("ix_doctors_specialization", "specialization"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), unique=True, nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False, index=True)
    specialization: Mapped[str] = mapped_column(String(120), nullable=False)
    qualification: Mapped[str | None] = mapped_column(String(255))
    experience: Mapped[int | None] = mapped_column(Integer)
    consultation_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    availability_status: Mapped[str] = mapped_column(String(30), nullable=False, default="AVAILABLE", server_default="AVAILABLE", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="doctor")
    department: Mapped["Department"] = relationship(back_populates="doctors")
    schedules: Mapped[list["DoctorSchedule"]] = relationship(back_populates="doctor", cascade="all, delete-orphan")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")
    medical_records: Mapped[list["MedicalRecord"]] = relationship(back_populates="doctor")
    prescriptions: Mapped[list["Prescription"]] = relationship(back_populates="doctor")


class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"
    __table_args__ = (Index("ix_doctor_schedules_doctor_day", "doctor_id", "day_of_week"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    appointment_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=30, server_default="30")
    break_start: Mapped[time | None] = mapped_column(Time)
    break_end: Mapped[time | None] = mapped_column(Time)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")

    doctor: Mapped["Doctor"] = relationship(back_populates="schedules")


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (UniqueConstraint("doctor_id", "appointment_date", "appointment_time", name="uq_doctor_appointment_slot"), Index("ix_appointments_patient_date", "patient_id", "appointment_date"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False, index=True)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_time: Mapped[time] = mapped_column(Time, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[AppointmentStatus] = mapped_column(String(20), nullable=False, default=AppointmentStatus.PENDING, server_default=AppointmentStatus.PENDING.value, index=True)
    consultation_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    payment_status: Mapped[PaymentStatus] = mapped_column(String(20), nullable=False, default=PaymentStatus.PENDING, server_default=PaymentStatus.PENDING.value, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    patient: Mapped["Patient"] = relationship(back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship(back_populates="appointments")
    medical_record: Mapped["MedicalRecord | None"] = relationship(back_populates="appointment", uselist=False)
    prescription: Mapped["Prescription | None"] = relationship(back_populates="appointment", uselist=False)
    bill: Mapped["Bill | None"] = relationship(back_populates="appointment", uselist=False)


class MedicalRecord(Base):
    __tablename__ = "medical_records"
    __table_args__ = (UniqueConstraint("appointment_id", name="uq_medical_record_appointment"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False, index=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id", ondelete="RESTRICT"), nullable=False)
    diagnosis: Mapped[str | None] = mapped_column(Text)
    symptoms: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    treatment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    patient: Mapped["Patient"] = relationship(back_populates="medical_records")
    doctor: Mapped["Doctor"] = relationship(back_populates="medical_records")
    appointment: Mapped["Appointment"] = relationship(back_populates="medical_record")


class Prescription(Base):
    __tablename__ = "prescriptions"
    __table_args__ = (UniqueConstraint("appointment_id", name="uq_prescription_appointment"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False, index=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id", ondelete="RESTRICT"), nullable=False)
    prescription_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    patient: Mapped["Patient"] = relationship(back_populates="prescriptions")
    doctor: Mapped["Doctor"] = relationship(back_populates="prescriptions")
    appointment: Mapped["Appointment"] = relationship(back_populates="prescription")
    items: Mapped[list["PrescriptionItem"]] = relationship(back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prescription_id: Mapped[int] = mapped_column(ForeignKey("prescriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    medicine: Mapped[str] = mapped_column(String(150), nullable=False)
    dosage: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency: Mapped[str] = mapped_column(String(100), nullable=False)
    duration: Mapped[str] = mapped_column(String(100), nullable=False)
    instructions: Mapped[str | None] = mapped_column(String(500))

    prescription: Mapped["Prescription"] = relationship(back_populates="items")


class Bill(Base):
    __tablename__ = "bills"
    __table_args__ = (UniqueConstraint("appointment_id", name="uq_bill_appointment"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id", ondelete="RESTRICT"), nullable=False)
    consultation_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    additional_charges: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    tax: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0.00")
    payment_status: Mapped[PaymentStatus] = mapped_column(String(20), nullable=False, default=PaymentStatus.PENDING, server_default=PaymentStatus.PENDING.value, index=True)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    patient: Mapped["Patient"] = relationship(back_populates="bills")
    appointment: Mapped["Appointment"] = relationship(back_populates="bill")
    payments: Mapped[list["Payment"]] = relationship(back_populates="bill", cascade="all, delete-orphan")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bill_id: Mapped[int] = mapped_column(ForeignKey("bills.id", ondelete="RESTRICT"), nullable=False, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    transaction_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    payment_status: Mapped[PaymentStatus] = mapped_column(String(20), nullable=False, default=PaymentStatus.PENDING, server_default=PaymentStatus.PENDING.value, index=True)
    payment_date: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    bill: Mapped["Bill"] = relationship(back_populates="payments")
    patient: Mapped["Patient"] = relationship(back_populates="payments")


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_user_read", "user_id", "read_status"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    read_status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="notifications")
