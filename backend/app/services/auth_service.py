from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Patient, Role, User
from app.schemas.auth import RegisterRequest
from app.core.security import hash_password, verify_password


class RegistrationConflictError(Exception):
    pass


class RegistrationConfigurationError(Exception):
    pass


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(
        select(User).options(joinedload(User.role)).where(User.email == email.lower())
    )


def register_patient(db: Session, request: RegisterRequest) -> User:
    email = request.email.lower()
    if get_user_by_email(db, email):
        raise RegistrationConflictError

    patient_role = db.scalar(select(Role).where(Role.name == "PATIENT"))
    if patient_role is None:
        raise RegistrationConfigurationError

    user = User(
        role=patient_role,
        email=email,
        password_hash=hash_password(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        phone=request.phone,
    )
    user.patient = Patient()
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise RegistrationConflictError from exc
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user
