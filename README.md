# Healthcare Management & Appointment System

A full-stack healthcare management and appointment system being developed in phases.

## Current Phase

Phases 1–13 are complete. The React frontend is connected to the FastAPI API client for authentication, dashboards, doctors, appointments, availability, and notifications. Backend API verification uses isolated test data; live MySQL remains blocked by invalid local credentials.

## Repository Layout

- `frontend/` - Existing React 19 + Vite JavaScript/JSX application
- `backend/` - Python 3.13 + FastAPI service and SQLAlchemy services
- `database/` - MySQL schema, seed data, and migrations
- `qa/` - Reserved for PyTest, Selenium, Requests, and database validation
- `docs/` - Reserved for project documentation

QA automation and CI/CD remain planned for later phases.

## Run the Frontend

```powershell
cd frontend
npm install
npm run lint
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/.env` when the API is not running at `http://127.0.0.1:8000`.

## Run the Backend

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API documentation is available at `http://127.0.0.1:8000/docs`. See [docs/api.md](docs/api.md) and [docs/setup.md](docs/setup.md) for workflows and configuration.
