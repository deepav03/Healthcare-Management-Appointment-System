import secrets

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.security import hash_password
from app.models import Department, Doctor, Role, User
from app.schemas.doctor import DoctorCreateRequest, DoctorUpdateRequest


class DoctorNotFoundError(Exception):
    pass


class DoctorConflictError(Exception):
    pass


class DepartmentNotFoundError(Exception):
    pass


def doctor_query():
    return select(Doctor).options(joinedload(Doctor.user), joinedload(Doctor.department))


def get_doctor(db: Session, doctor_id: int) -> Doctor | None:
    return db.scalar(doctor_query().where(Doctor.id == doctor_id))


def list_doctors(
    db: Session,
    search: str | None = None,
    specialization: str | None = None,
    department_id: int | None = None,
    active: bool | None = None,
) -> list[Doctor]:
    statement = doctor_query().join(Doctor.user).join(Doctor.department)
    if search:
        value = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                User.first_name.ilike(value),
                User.last_name.ilike(value),
                User.email.ilike(value),
                Doctor.specialization.ilike(value),
            )
        )
    if specialization:
        statement = statement.where(Doctor.specialization.ilike(specialization.strip()))
    if department_id is not None:
        statement = statement.where(Doctor.department_id == department_id)
    if active is not None:
        statement = statement.where(User.is_active == active)
    return list(db.scalars(statement.order_by(Doctor.id)).unique().all())


def create_doctor(db: Session, request: DoctorCreateRequest) -> Doctor:
    department = db.get(Department, request.department_id)
    if department is None:
        raise DepartmentNotFoundError
    doctor_role = db.scalar(select(Role).where(Role.name == "DOCTOR"))
    if doctor_role is None:
        raise DoctorConflictError

    data = request.model_dump()
    availability = data.pop("availability_status").value
    user = User(
        role=doctor_role,
        email=str(request.email).lower(),
        phone=request.phone,
        first_name=request.first_name,
        last_name=request.last_name,
        password_hash=hash_password(secrets.token_urlsafe(32)),
        is_active=availability == "AVAILABLE",
    )
    doctor = Doctor(
        user=user,
        department=department,
        specialization=request.specialization,
        qualification=request.qualification,
        experience=request.experience,
        consultation_fee=request.consultation_fee,
        availability_status=availability,
    )
    db.add(doctor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DoctorConflictError from exc
    return get_doctor(db, doctor.id)


def update_doctor(db: Session, doctor_id: int, request: DoctorUpdateRequest) -> Doctor:
    doctor = get_doctor(db, doctor_id)
    if doctor is None:
        raise DoctorNotFoundError
    updates = request.model_dump(exclude_unset=True)
    if "department_id" in updates:
        department = db.get(Department, updates["department_id"])
        if department is None:
            raise DepartmentNotFoundError
    for field, value in updates.items():
        if field in {"first_name", "last_name", "email", "phone"}:
            setattr(doctor.user, field, str(value).lower() if field == "email" else value)
        elif field == "availability_status":
            doctor.availability_status = value.value
            doctor.user.is_active = value.value == "AVAILABLE"
        else:
            setattr(doctor, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DoctorConflictError from exc
    return get_doctor(db, doctor_id)


def set_doctor_active(db: Session, doctor_id: int, active: bool) -> Doctor:
    doctor = get_doctor(db, doctor_id)
    if doctor is None:
        raise DoctorNotFoundError
    doctor.user.is_active = active
    doctor.availability_status = "AVAILABLE" if active else "UNAVAILABLE"
    db.commit()
    return get_doctor(db, doctor_id)
