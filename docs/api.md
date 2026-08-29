# API Inventory

OpenAPI UI: `http://127.0.0.1:8000/docs`  
OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

All routes below except `/health` require `Authorization: Bearer <access-token>`. The bearer scheme and request/response models are generated from the actual FastAPI application.

## Authentication

- `POST /api/auth/register` | public | Creates a PATIENT account; invalid data `422`, duplicate email/phone `409`.
- `POST /api/auth/login` | public | Returns JWT; invalid or inactive credentials `401`.
- `GET /api/auth/me` | authenticated | Returns safe current-user data.
- `POST /api/auth/logout` | authenticated | Stateless logout acknowledgement; client discards the token.
- `GET /api/auth/admin-check` | ADMIN
- `GET /api/auth/doctor-check` | DOCTOR
- `GET /api/auth/patient-check` | PATIENT

## Patients

- `GET /api/patients/me` | PATIENT | Own profile.
- `GET /api/patients` | ADMIN, DOCTOR | Search with `query` and `status`.
- `GET /api/patients/{patient_id}` | authenticated | Patients only see themselves; ADMIN/DOCTOR can view.
- `PATCH /api/patients/{patient_id}` | own PATIENT or ADMIN | Updates validated profile fields.
- `POST /api/patients/{patient_id}/deactivate` | ADMIN | Deactivates patient and user.

## Doctors and schedules

- `GET /api/doctors` | authenticated | Search/filter with `search`, `specialization`, `department`, `active`.
- `POST /api/doctors` | ADMIN | Creates a doctor user/profile.
- `GET /api/doctors/{doctor_id}` | authenticated | Patients see active doctors.
- `PATCH /api/doctors/{doctor_id}` | own DOCTOR or ADMIN | Updates doctor profile.
- `POST /api/doctors/{doctor_id}/activate` | ADMIN
- `POST /api/doctors/{doctor_id}/deactivate` | ADMIN
- `GET /api/doctors/{doctor_id}/schedules` | ADMIN, own DOCTOR, active-doctor PATIENT view
- `POST /api/doctors/{doctor_id}/schedules` | ADMIN or own DOCTOR | Validates weekday, time, break, and overlap.
- `PATCH /api/schedules/{schedule_id}` | ADMIN or owning DOCTOR
- `DELETE /api/schedules/{schedule_id}` | ADMIN or owning DOCTOR | `204` on success.
- `GET /api/doctors/{doctor_id}/availability` | authorized schedule viewer | Weekly schedules.
- `GET /api/doctors/{doctor_id}/availability/{date}` | authorized schedule viewer | Generated slots; past date `400`.

## Appointments

- `POST /api/appointments` | PATIENT | Uses JWT patient identity, validates active doctor/slot, starts `PENDING`.
- `GET /api/appointments/my` | PATIENT or DOCTOR | Own appointments.
- `GET /api/appointments` | ADMIN | Filters: `patient_id`, `doctor_id`, `date`, `status`.
- `GET /api/appointments/{appointment_id}` | owner DOCTOR/PATIENT or ADMIN
- `PATCH /api/appointments/{appointment_id}/confirm` | owning DOCTOR
- `PATCH /api/appointments/{appointment_id}/reject` | owning DOCTOR
- `PATCH /api/appointments/{appointment_id}/complete` | owning DOCTOR
- `PATCH /api/appointments/{appointment_id}/cancel` | owner or ADMIN | Completed appointments cannot be cancelled.
- `PATCH /api/appointments/{appointment_id}/reschedule` | owning PATIENT | Validates future available, unbooked slot.

## Clinical records and prescriptions

- `POST /api/medical-records` | DOCTOR, ADMIN | Completed matching appointment required.
- `GET /api/medical-records` | scoped PATIENT/DOCTOR or ADMIN
- `GET /api/medical-records/{record_id}` | scoped owner or ADMIN
- `GET /api/patients/{patient_id}/medical-records` | scoped PATIENT/DOCTOR or ADMIN
- `PATCH /api/medical-records/{record_id}` | owning DOCTOR or ADMIN
- `POST /api/prescriptions` | DOCTOR, ADMIN | Completed matching appointment; prescription plus items is one transaction.
- `GET /api/prescriptions` | scoped PATIENT/DOCTOR or ADMIN
- `GET /api/prescriptions/{prescription_id}` | scoped owner or ADMIN
- `GET /api/patients/{patient_id}/prescriptions` | scoped PATIENT/DOCTOR or ADMIN

## Billing and simulated payments

- `POST /api/bills` | ADMIN, DOCTOR | Server-calculates consultation fee plus charges minus discount plus tax.
- `GET /api/bills` | PATIENT or ADMIN
- `GET /api/bills/{bill_id}` | owning PATIENT or ADMIN
- `GET /api/patients/{patient_id}/bills` | own PATIENT or ADMIN
- `POST /api/payments` | PATIENT | Simulated `UPI`, `CARD`, or `CASH`; deterministic `SUCCESS` or `FAILED` outcome.
- `GET /api/payments` | PATIENT or ADMIN
- `GET /api/payments/{payment_id}` | owning PATIENT or ADMIN
- `GET /api/bills/{bill_id}/payments` | owning PATIENT or ADMIN

## Notifications, dashboards, and reports

- `GET /api/notifications` | authenticated | Own notifications only.
- `GET /api/notifications/{notification_id}` | owner only
- `PATCH /api/notifications/{notification_id}/read` | owner only
- `PATCH /api/notifications/read-all` | authenticated
- `GET /api/dashboard/admin` | ADMIN
- `GET /api/dashboard/doctor` | DOCTOR
- `GET /api/dashboard/patient` | PATIENT
- `GET /api/reports/appointments` | ADMIN | Optional `start_date`, `end_date`, `doctor_id`, `status`.
- `GET /api/reports/revenue` | ADMIN | Optional `start_date`, `end_date`.
- `GET /api/reports/payments` | ADMIN | Optional `start_date`, `end_date`.
- `GET /api/reports/patients` | ADMIN

## Response conventions

- `200` successful reads/updates
- `201` successful creates
- `204` successful schedule deletion
- `400` business-rule violation
- `401` missing/invalid JWT
- `403` insufficient role or ownership
- `404` missing resource
- `409` duplicate/conflicting business data
- `422` request validation failure

No raw stack traces, password hashes, or payment gateway data are returned.
