from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.api.dependencies import require_authenticated_user, require_roles
from app.db.session import get_db
from app.models import User
from app.schemas.reporting import DashboardResponse, NotificationResponse, ReportResponse
from app.services.notification_service import get_notification, list_notifications, mark_all_read, mark_read
from app.services.reporting_service import admin_dashboard, appointment_report, doctor_dashboard, patient_dashboard, patient_report, payment_report, revenue_report

router = APIRouter(tags=["notifications", "dashboards", "reports"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(require_authenticated_user)]


def notification_response(item):
    return NotificationResponse.model_validate(item, from_attributes=True)


def user_id(user: User) -> int:
    return user.id


@router.get("/api/notifications", response_model=list[NotificationResponse])
def notifications(current_user: CurrentUser, db: DbSession):
    return [notification_response(item) for item in list_notifications(db, user_id(current_user))]


@router.get("/api/notifications/{notification_id}", response_model=NotificationResponse)
def notification_detail(notification_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    item = get_notification(db, notification_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    if item.user_id != user_id(current_user):
        raise HTTPException(status_code=403, detail="Notification access denied")
    return notification_response(item)


@router.patch("/api/notifications/{notification_id}/read", response_model=NotificationResponse)
def read_notification(notification_id: Annotated[int, Path(ge=1)], current_user: CurrentUser, db: DbSession):
    item = get_notification(db, notification_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    if item.user_id != user_id(current_user):
        raise HTTPException(status_code=403, detail="Notification access denied")
    return notification_response(mark_read(db, notification_id))


@router.patch("/api/notifications/read-all")
def read_all_notifications(current_user: CurrentUser, db: DbSession):
    return {"updated": mark_all_read(db, user_id(current_user))}


@router.get("/api/dashboard/admin", response_model=DashboardResponse)
def admin_dashboard_endpoint(current_user: Annotated[User, Depends(require_roles("ADMIN"))], db: DbSession):
    return DashboardResponse(data=admin_dashboard(db))


@router.get("/api/dashboard/doctor", response_model=DashboardResponse)
def doctor_dashboard_endpoint(current_user: Annotated[User, Depends(require_roles("DOCTOR"))], db: DbSession):
    if current_user.doctor is None:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return DashboardResponse(data=doctor_dashboard(db, current_user.doctor.id))


@router.get("/api/dashboard/patient", response_model=DashboardResponse)
def patient_dashboard_endpoint(current_user: Annotated[User, Depends(require_roles("PATIENT"))], db: DbSession):
    if current_user.patient is None:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return DashboardResponse(data=patient_dashboard(db, current_user.patient.id, current_user.id))


@router.get("/api/reports/appointments", response_model=ReportResponse)
def appointments_report(
    current_user: Annotated[User, Depends(require_roles("ADMIN"))], db: DbSession,
    start_date: date | None = None, end_date: date | None = None,
    doctor_id: Annotated[int | None, Query(gt=0)] = None,
    appointment_status: Annotated[str | None, Query(alias="status")] = None,
):
    return ReportResponse(data=appointment_report(db, start_date, end_date, doctor_id, appointment_status))


@router.get("/api/reports/revenue", response_model=ReportResponse)
def revenue(
    current_user: Annotated[User, Depends(require_roles("ADMIN"))], db: DbSession,
    start_date: date | None = None, end_date: date | None = None,
):
    return ReportResponse(data=revenue_report(db, start_date, end_date))


@router.get("/api/reports/payments", response_model=ReportResponse)
def payments(
    current_user: Annotated[User, Depends(require_roles("ADMIN"))], db: DbSession,
    start_date: date | None = None, end_date: date | None = None,
):
    return ReportResponse(data=payment_report(db, start_date, end_date))


@router.get("/api/reports/patients", response_model=ReportResponse)
def patients_report(current_user: Annotated[User, Depends(require_roles("ADMIN"))], db: DbSession):
    return ReportResponse(data=patient_report(db))
