# Local Setup

Phases 1–13 provide a React frontend integrated with the FastAPI REST API. The frontend API base URL is configured with `VITE_API_BASE_URL`.

## Backend

Use Python 3.13 in Windows PowerShell:

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set a long random `JWT_SECRET_KEY` in `.env` for local use. Configure either `DATABASE_URL` or the individual `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` values.

For the frontend:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run lint
npm run build
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## MySQL

MySQL 8.0+ must be running for real registration/login and seeded-user verification. From the repository root:

```powershell
mysql -u healthcare_user -p healthcare_db < database/schema.sql
mysql -u healthcare_user -p healthcare_db < database/seed.sql
```

No database is recreated or destroyed automatically.

## Authentication

- `POST /api/auth/register` creates a PATIENT user and patient record.
- `POST /api/auth/login` returns a short-lived JWT access token.
- `GET /api/auth/me` requires `Authorization: Bearer <token>`.
- `POST /api/auth/logout` acknowledges stateless logout; the client discards the token.
- `/api/auth/admin-check`, `/api/auth/doctor-check`, and `/api/auth/patient-check` demonstrate role authorization.

Passwords are bcrypt-hashed and are never returned by the API. Invalid credentials return 401, insufficient roles return 403, duplicate registration returns 409, and invalid request data returns 422.

## Local Demo Credentials

The fictional seed accounts use the bcrypt hash in `database/seed.sql` and the local-only password `ChangeMe123!`:

```text
admin.demo@example.com   ADMIN
maya.patel@example.com   DOCTOR
james.chen@example.com   DOCTOR
aiden.ross@example.com   DOCTOR
olivia.bennett@example.com PATIENT
```

Do not use these credentials in a real environment.

## Tests

Run all backend tests:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

The authentication tests use isolated SQLite data for deterministic API testing. They are separate from live MySQL integration. A configured MySQL server is required to verify the seeded accounts against actual database tables.
