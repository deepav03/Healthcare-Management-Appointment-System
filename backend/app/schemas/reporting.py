from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    notification_type: str
    message: str
    read_status: bool
    created_at: datetime


class DashboardResponse(BaseModel):
    data: dict[str, int | str | Decimal | None]


class ReportResponse(BaseModel):
    data: list[dict[str, int | str | Decimal | date | None]]
