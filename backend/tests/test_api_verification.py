from app.main import app


EXPECTED_METHODS = {
    ("/health", "GET"),
    ("/api/auth/register", "POST"),
    ("/api/auth/login", "POST"),
    ("/api/auth/me", "GET"),
    ("/api/auth/logout", "POST"),
    ("/api/patients", "GET"),
    ("/api/patients/me", "GET"),
    ("/api/patients/{patient_id}", "GET"),
    ("/api/patients/{patient_id}", "PATCH"),
    ("/api/patients/{patient_id}/deactivate", "POST"),
    ("/api/doctors", "GET"),
    ("/api/doctors", "POST"),
    ("/api/doctors/{doctor_id}", "GET"),
    ("/api/doctors/{doctor_id}", "PATCH"),
    ("/api/doctors/{doctor_id}/activate", "POST"),
    ("/api/doctors/{doctor_id}/deactivate", "POST"),
    ("/api/doctors/{doctor_id}/schedules", "GET"),
    ("/api/doctors/{doctor_id}/schedules", "POST"),
    ("/api/schedules/{schedule_id}", "PATCH"),
    ("/api/schedules/{schedule_id}", "DELETE"),
    ("/api/doctors/{doctor_id}/availability", "GET"),
    ("/api/doctors/{doctor_id}/availability/{availability_date}", "GET"),
    ("/api/appointments", "GET"),
    ("/api/appointments", "POST"),
    ("/api/appointments/my", "GET"),
    ("/api/appointments/{appointment_id}", "GET"),
    ("/api/appointments/{appointment_id}/confirm", "PATCH"),
    ("/api/appointments/{appointment_id}/reject", "PATCH"),
    ("/api/appointments/{appointment_id}/complete", "PATCH"),
    ("/api/appointments/{appointment_id}/cancel", "PATCH"),
    ("/api/appointments/{appointment_id}/reschedule", "PATCH"),
    ("/api/medical-records", "GET"),
    ("/api/medical-records", "POST"),
    ("/api/medical-records/{record_id}", "GET"),
    ("/api/medical-records/{record_id}", "PATCH"),
    ("/api/prescriptions", "GET"),
    ("/api/prescriptions", "POST"),
    ("/api/prescriptions/{prescription_id}", "GET"),
    ("/api/bills", "GET"),
    ("/api/bills", "POST"),
    ("/api/bills/{bill_id}", "GET"),
    ("/api/payments", "GET"),
    ("/api/payments", "POST"),
    ("/api/payments/{payment_id}", "GET"),
    ("/api/notifications", "GET"),
    ("/api/notifications/{notification_id}", "GET"),
    ("/api/notifications/{notification_id}/read", "PATCH"),
    ("/api/notifications/read-all", "PATCH"),
    ("/api/dashboard/admin", "GET"),
    ("/api/dashboard/doctor", "GET"),
    ("/api/dashboard/patient", "GET"),
    ("/api/reports/appointments", "GET"),
    ("/api/reports/revenue", "GET"),
    ("/api/reports/payments", "GET"),
    ("/api/reports/patients", "GET"),
}


def test_expected_api_routes_and_methods_are_registered():
    actual = {
        (path, method.upper())
        for path, operations in app.openapi()["paths"].items()
        for method in operations
        if method in {"get", "post", "patch", "delete", "put"}
    }
    assert EXPECTED_METHODS <= actual


def test_openapi_contains_request_and_response_schemas():
    spec = app.openapi()
    assert spec["components"]["securitySchemes"]["HTTPBearer"]["scheme"] == "bearer"
    for path, method in (("/api/auth/login", "post"), ("/api/appointments", "post"), ("/api/bills", "post")):
        operation = spec["paths"][path][method]
        assert "responses" in operation
        assert "200" in operation["responses"] or "201" in operation["responses"]
        assert "requestBody" in operation


def test_protected_operations_declare_bearer_security():
    spec = app.openapi()
    for path, method in (("/api/auth/me", "get"), ("/api/patients/me", "get"), ("/api/dashboard/admin", "get")):
        assert spec["paths"][path][method]["security"] == [{"HTTPBearer": []}]
