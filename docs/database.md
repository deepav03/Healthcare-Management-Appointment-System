# Database Foundation

Phase 3 uses MySQL 8.0+ with SQLAlchemy 2.x and the PyMySQL driver. The application does not create or destroy tables during startup.

## Prerequisites

Install MySQL Server 8.0 or later and make sure the MySQL client is available in PowerShell. Create a local database and user:

```powershell
mysql -u root -p
```

```sql
CREATE DATABASE healthcare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'healthcare_user'@'localhost' IDENTIFIED BY 'change-me';
GRANT ALL PRIVILEGES ON healthcare_db.* TO 'healthcare_user'@'localhost';
FLUSH PRIVILEGES;
```

Use a development-only password. Never commit real credentials.

## Environment

From `backend/`, create a local environment file:

```powershell
cd backend
Copy-Item .env.example .env
```

Configure `DATABASE_URL`, or configure the individual values:

```text
DB_HOST=localhost
DB_PORT=3306
DB_NAME=healthcare_db
DB_USER=healthcare_user
DB_PASSWORD=change-me
```

`DATABASE_URL` takes precedence when it is non-empty. `CORS_ORIGINS` accepts a comma-separated list.

## Schema Setup

Apply the schema from the repository root:

```powershell
mysql -u healthcare_user -p healthcare_db < database/schema.sql
```

Load fictional demonstration data only after the schema exists:

```powershell
mysql -u healthcare_user -p healthcare_db < database/seed.sql
```

The seed accounts use bcrypt-formatted demonstration hashes and fictional data. They are not production credentials.

## SQLAlchemy Initialization

For local development, SQLAlchemy can create missing tables without dropping existing tables:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.db.init_db
```

This command requires a reachable MySQL database and uses the configured environment variables. It is intentionally not called from `app.main`.

## Verification

Verify tables through MySQL:

```powershell
mysql -u healthcare_user -p -D healthcare_db -e "SHOW TABLES;"
mysql -u healthcare_user -p -D healthcare_db -e "SELECT COUNT(*) AS users FROM users;"
```

Verify the ORM metadata without MySQL:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q tests/test_database_foundation.py
```

The metadata tests do not claim that MySQL is available. Live database verification requires a configured MySQL server and is intentionally separate.

## Phase 7 Schedule Migration

The original foundation schema used a unique `(doctor_id, day_of_week)` constraint. Phase 7 replaces it with a normal index so a doctor may have multiple non-overlapping shifts on one day. New installations get the correct definition from `database/schema.sql`. Existing MySQL installations should apply this change after confirming the constraint name:

```sql
ALTER TABLE doctor_schedules DROP INDEX uq_doctor_schedule_day;
CREATE INDEX ix_doctor_schedules_doctor_day ON doctor_schedules (doctor_id, day_of_week);
```

Schedule overlap and duplicate-range validation is enforced by the application service.
