from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Notification


def create_notification(db: Session, user_id: int, notification_type: str, message: str) -> Notification:
    notification = Notification(user_id=user_id, notification_type=notification_type, message=message)
    db.add(notification)
    db.flush()
    return notification


def list_notifications(db: Session, user_id: int) -> list[Notification]:
    return list(db.scalars(select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())).all())


def get_notification(db: Session, notification_id: int) -> Notification | None:
    return db.get(Notification, notification_id)


def mark_read(db: Session, notification_id: int) -> Notification | None:
    notification = get_notification(db, notification_id)
    if notification is None:
        return None
    notification.read_status = True
    db.commit()
    return notification


def mark_all_read(db: Session, user_id: int) -> int:
    notifications = list_notifications(db, user_id)
    for notification in notifications:
        notification.read_status = True
    db.commit()
    return len(notifications)
