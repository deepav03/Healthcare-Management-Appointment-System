import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "qa" / ".env")


@dataclass(frozen=True)
class QAConfig:
    ui_base_url: str = os.getenv("UI_BASE_URL", "http://127.0.0.1:5173")
    api_base_url: str = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
    browser: str = os.getenv("BROWSER", "chrome")
    headless: bool = os.getenv("HEADLESS", "true").lower() == "true"
    explicit_wait_seconds: int = int(os.getenv("EXPLICIT_WAIT_SECONDS", "10"))
    screenshot_dir: Path = ROOT / os.getenv("SCREENSHOT_DIR", "qa/screenshots")
    run_ui: bool = os.getenv("QA_RUN_UI", "false").lower() == "true"
    run_live_api: bool = os.getenv("QA_RUN_LIVE_API", "false").lower() == "true"
    run_live_db: bool = os.getenv("QA_RUN_LIVE_DB", "false").lower() == "true"
    patient_email: str = os.getenv("TEST_PATIENT_EMAIL", "")
    patient_password: str = os.getenv("TEST_PATIENT_PASSWORD", "")
    doctor_email: str = os.getenv("TEST_DOCTOR_EMAIL", "")
    doctor_password: str = os.getenv("TEST_DOCTOR_PASSWORD", "")
    admin_email: str = os.getenv("TEST_ADMIN_EMAIL", "")
    admin_password: str = os.getenv("TEST_ADMIN_PASSWORD", "")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_name: str = os.getenv("DB_NAME", "healthcare_db")
    db_user: str = os.getenv("DB_USER", "healthcare_user")
    db_password: str = os.getenv("DB_PASSWORD", "")


config = QAConfig()
