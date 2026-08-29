from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin, require_authenticated_user, require_doctor, require_patient
from app.core.security import create_access_token
from app.db.session import get_db
from app.models import User
from app.schemas.auth import LoginRequest, MessageResponse, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import (
    RegistrationConflictError,
    RegistrationConfigurationError,
    authenticate_user,
    register_patient,
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])
DbSession = Annotated[Session, Depends(get_db)]


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.name,
        is_active=user.is_active,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: DbSession):
    try:
        user = register_patient(db, request)
    except RegistrationConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or phone is already registered") from exc
    except RegistrationConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Patient registration is not configured") from exc
    return to_user_response(user)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: DbSession):
    user = authenticate_user(db, request.email, request.password)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, expires_in = create_access_token(user.id, user.role.name)
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=UserResponse)
def current_user(current_user: Annotated[User, Depends(require_authenticated_user)]):
    return to_user_response(current_user)


@router.post("/logout", response_model=MessageResponse)
def logout(current_user: Annotated[User, Depends(require_authenticated_user)]):
    return MessageResponse(message="Logout acknowledged; discard the bearer token on the client")


@router.get("/admin-check", response_model=MessageResponse)
def admin_check(current_user: Annotated[User, Depends(require_admin)]):
    return MessageResponse(message="Admin authorization granted")


@router.get("/doctor-check", response_model=MessageResponse)
def doctor_check(current_user: Annotated[User, Depends(require_doctor)]):
    return MessageResponse(message="Doctor authorization granted")


@router.get("/patient-check", response_model=MessageResponse)
def patient_check(current_user: Annotated[User, Depends(require_patient)]):
    return MessageResponse(message="Patient authorization granted")
