# Backend

FastAPI foundation for the Healthcare Management & Appointment System.

## Requirements

- Python 3.13
- MySQL 8.0+

## Setup on Windows PowerShell

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Update `.env` with local MySQL connection details. `DATABASE_URL` may be used directly, or `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` may be configured separately.

JWT settings are also environment-based:

```text
JWT_SECRET_KEY=replace-with-a-long-random-local-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Initialize the database

From the repository root, apply the schema and fictional demo data:

```powershell
mysql -u healthcare_user -p healthcare_db < database/schema.sql
mysql -u healthcare_user -p healthcare_db < database/seed.sql
```

Alternatively, with `.env` configured and a reachable MySQL server, create missing tables through SQLAlchemy without dropping existing data:

```powershell
python -m app.db.init_db
```

## Start the API

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health endpoint: `http://127.0.0.1:8000/health`

## Authentication API

Register a patient:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/auth/register -ContentType 'application/json' -Body (@{
	first_name = 'Demo'
	last_name = 'Patient'
	email = 'demo.patient@example.com'
	phone = '5550009999'
	password = 'StrongPass1!'
	password_confirmation = 'StrongPass1!'
} | ConvertTo-Json)
```

Login and capture the access token:

```powershell
$login = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/auth/login -ContentType 'application/json' -Body (@{
	email = 'demo.patient@example.com'
	password = 'StrongPass1!'
} | ConvertTo-Json)
$headers = @{ Authorization = "Bearer $($login.access_token)" }
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/auth/me -Headers $headers
```

Protected role checks are available at `/api/auth/admin-check`, `/api/auth/doctor-check`, and `/api/auth/patient-check`. Logout is stateless: the client must discard the bearer token; no server-side token revocation is claimed.

Local seed credentials use the fictional accounts in `database/seed.sql` with password `ChangeMe123!`. Do not use them outside local demonstrations.

## Run tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

The model, metadata, and authentication tests use isolated test data and do not require MySQL. They do not claim that seeded users work against a live database. A live MySQL connection is required for `python -m app.db.init_db`, the SQL scripts, and real seeded-user authentication.

The API also includes the Phase 9-11 clinical, billing, simulated payment, notification, dashboard, and reporting endpoints. See `docs/api.md` and the generated OpenAPI page at `/docs`.

## Appointment API

Appointment creation is restricted to authenticated patients. The patient is derived from the JWT; any supplied `patient_id` must match that identity. Doctors can manage only appointments assigned to them, while admins can list and filter all appointments.

Endpoints:

- `POST /api/appointments`
- `GET /api/appointments/my`
- `GET /api/appointments`
- `GET /api/appointments/{appointment_id}`
- `PATCH /api/appointments/{appointment_id}/confirm`
- `PATCH /api/appointments/{appointment_id}/reject`
- `PATCH /api/appointments/{appointment_id}/complete`
- `PATCH /api/appointments/{appointment_id}/cancel`
- `PATCH /api/appointments/{appointment_id}/reschedule`

New appointments are `PENDING`. Legal transitions are enforced in the service layer. Slot validation reuses the doctor schedule generator, and the existing unique database constraint on doctor/date/time is caught and returned as `409 Conflict`.
