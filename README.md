# Healthcare Management & Appointment System

A full-stack healthcare management application for patient registration, secure authentication, doctor discovery, appointment scheduling, clinical records, prescriptions, billing, payments, notifications, dashboards, and reports.

The project uses a React frontend, a FastAPI backend, and a MySQL relational database. The frontend communicates with the backend through a JSON REST API secured with JWT bearer tokens and role-based authorization.

## Features

### Authentication and users

- Patient registration with email, phone, password-strength, and confirmation validation.
- Login with JWT access tokens.
- Current-user and logout endpoints.
- Role checks for ADMIN, DOCTOR, and PATIENT users.
- Bcrypt password hashing; passwords and password hashes are never returned by the API.
- Readable frontend handling for FastAPI validation errors.

### Patients and doctors

- Patient profile viewing and updates.
- Doctor listing with search and filters.
- Doctor profile details.
- Doctor activation and deactivation for administrators.
- Doctor schedules with weekday, time, break, overlap, and availability validation.
- Generated appointment availability slots.

### Appointments

- Patient-only appointment creation.
- Future-date validation; past appointments are rejected.
- Doctor schedule and time-slot validation.
- Duplicate slot protection.
- Appointment listing for patients and doctors.
- Appointment confirmation, rejection, completion, cancellation, and rescheduling.
- Ownership and role-based access control.

### Clinical and financial workflows

- Medical records linked to completed appointments.
- Prescriptions and prescription items.
- Bills with server-calculated totals.
- Simulated payments using UPI, CARD, or CASH.
- Patient-scoped notifications and read-status management.
- Patient, doctor, and administrator dashboards.
- Administrator reports for appointments, revenue, payments, and patients.

## Technology Stack and Skills Used

### Frontend

- React 19
- JavaScript and JSX
- Vite 8
- `lucide-react` icons
- Fetch-based API client
- Browser session storage for the access token
- Oxlint for frontend linting

### Backend

- Python 3.13
- FastAPI
- Uvicorn
- Pydantic and Pydantic Settings
- SQLAlchemy 2
- PyMySQL
- JWT with PyJWT
- Bcrypt password hashing
- CORS configuration for local and deployed frontend origins

### Database and quality

- MySQL 8+
- Relational schema with foreign keys, indexes, and uniqueness constraints
- SQL seed data containing fictional demonstration users and records
- Pytest API, service, model, validation, and database-foundation tests
- Selenium, Requests, and database QA scaffolding in `qa/`
- PowerShell-based local development and verification workflow

## Project Structure

```text
HEALTHCARE-MANAGEMENT-APPOINTMENTSYSTEM/
|
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |   |-- dependencies.py
|   |   |   `-- routes/
|   |   |-- core/
|   |   |   |-- config.py
|   |   |   `-- security.py
|   |   |-- db/
|   |   |   |-- init_db.py
|   |   |   `-- session.py
|   |   |-- models/
|   |   |-- schemas/
|   |   `-- services/
|   |-- tests/
|   |-- .env.example
|   |-- README.md
|   `-- requirements.txt
|
|-- frontend/
|   |-- public/
|   |-- src/
|   |   |-- api/
|   |   |-- assets/
|   |   |-- App.jsx
|   |   |-- IntegratedApp.jsx
|   |   |-- App.css
|   |   `-- index.css
|   |-- .env.example
|   |-- index.html
|   |-- package.json
|   `-- vite.config.js
|
|-- database/
|   |-- schema.sql
|   `-- seed.sql
|
|-- docs/
|   |-- api.md
|   |-- database.md
|   `-- setup.md
|
|-- qa/
|   |-- api/
|   |-- config/
|   |-- database/
|   |-- pages/
|   |-- tests/
|   |-- utils/
|   |-- .env.example
|   `-- pytest.ini
|
|-- .gitignore
`-- README.md
```

## Prerequisites

- Python 3.13
- Node.js and npm
- MySQL 8.0 or later
- Git

The backend uses the repository-level virtual environment at `.venv` in the recommended local setup. Never commit virtual environments, dependency directories, environment files, or generated build output.

## Local Setup

### 1. Configure the backend

From the repository root:

```powershell
cd backend
Copy-Item .env.example .env
```

Edit `backend/.env` with local values. The expected database settings are:

```text
DB_HOST=localhost
DB_PORT=3306
DB_NAME=healthcare_db
DB_USER=healthcare_user
DB_PASSWORD=<your-local-password>
JWT_SECRET_KEY=<long-random-local-secret>
```

Alternatively, provide a complete `DATABASE_URL`. Never commit `.env` or real credentials.

### 2. Create and initialize MySQL

Create the database and user with credentials appropriate for your local installation. Then, from the repository root, apply the schema and fictional seed data:

```powershell
mysql -u healthcare_user -p healthcare_db < database/schema.sql
mysql -u healthcare_user -p healthcare_db < database/seed.sql
```

The application does not drop or recreate database tables during startup. See [docs/database.md](docs/database.md) for the database model and verification commands.

### 3. Install and run the backend

```powershell
cd backend
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend endpoints:

- Health: `http://127.0.0.1:8000/health`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

### 4. Configure and run the frontend

Open a second terminal:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

The frontend is available at `http://127.0.0.1:5173/`. Its default API URL is `http://127.0.0.1:8000`; override it with `VITE_API_BASE_URL` in `frontend/.env` when needed.

The backend allows both local development origins:

- `http://127.0.0.1:5173`
- `http://localhost:5173`

## Demo Accounts

The seed file contains fictional demonstration accounts. The seed documentation identifies the local demo password. Change or remove these accounts before using any shared or production environment.

Never use demonstration credentials outside local development.

## Testing

### Backend tests

Backend tests use isolated test data where appropriate and do not replace live MySQL verification:

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest -q
```

The current backend suite has 99 passing tests with one dependency deprecation warning in the local environment.

### Frontend checks

```powershell
cd frontend
npm run lint
npm run build
```

### QA suite

The `qa/` directory contains API helpers, Selenium page objects, database helpers, configuration, and reporting support:

```powershell
cd qa
..\.venv\Scripts\python.exe -m pytest -q
```

The QA framework is prepared for expansion, but executable test cases must be added under `qa/tests` before it can provide automated Selenium or live API coverage.

### Manual smoke test

With MySQL, the backend, and the frontend running:

1. Register a new patient.
2. Log in and confirm the patient dashboard loads.
3. View doctors and doctor availability.
4. Book an available future appointment slot.
5. Confirm the appointment appears in the patient list.
6. Try the same slot again and verify a conflict response.
7. Try a past date and verify it is rejected.
8. Cancel the appointment.
9. Log out and confirm the session token is discarded.

## API Documentation

The complete route inventory, roles, request behavior, and response conventions are documented in [docs/api.md](docs/api.md). The live OpenAPI documentation is available at `http://127.0.0.1:8000/docs` when the backend is running.

## Security Notes

- Store credentials and JWT secrets in environment variables.
- Keep `.env`, database passwords, API keys, and tokens out of Git.
- Use a strong, unique `JWT_SECRET_KEY` outside local development.
- Use HTTPS and a restricted `CORS_ORIGINS` list when deployed.
- Replace fictional seed credentials before sharing a deployed environment.
- Do not expose SQLAlchemy or database stack traces to clients.

The repository `.gitignore` excludes `.env`, virtual environments, `node_modules`, build output, Python caches, pytest caches, logs, and local artifacts while allowing `.env.example` templates to remain documented.

## Deployment Notes

For public deployment, host the frontend and backend separately or in managed services, and use a managed MySQL-compatible database. Configure the deployed frontend URL in backend `CORS_ORIGINS` and set `VITE_API_BASE_URL` to the deployed backend URL. Keep all production secrets in the hosting provider's environment-variable configuration.

Do not publish local database credentials or commit a production `.env` file.

## Additional Documentation

- [Backend guide](backend/README.md)
- [Frontend guide](frontend/README.md)
- [API inventory](docs/api.md)
- [Database guide](docs/database.md)
- [Local setup guide](docs/setup.md)
