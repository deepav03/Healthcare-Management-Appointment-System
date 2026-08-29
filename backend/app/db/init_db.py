from app.db.session import Base, engine
import app.models  # noqa: F401 - imports models before metadata creation


def init_db() -> None:
    """Create missing tables without dropping or recreating existing data."""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables initialized.")
