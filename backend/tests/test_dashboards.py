from conftest import token_headers


def test_role_dashboards_return_scoped_statistics(business_client):
    admin = business_client.get("/api/dashboard/admin", headers=token_headers(1, "ADMIN"))
    doctor = business_client.get("/api/dashboard/doctor", headers=token_headers(2, "DOCTOR"))
    patient = business_client.get("/api/dashboard/patient", headers=token_headers(3, "PATIENT"))
    assert admin.status_code == doctor.status_code == patient.status_code == 200
    assert admin.json()["data"]["total_patients"] == 1
    assert doctor.json()["data"]["completed_appointments"] == 1
    assert patient.json()["data"]["appointment_count"] == 1


def test_dashboard_requires_role(business_client):
    assert business_client.get("/api/dashboard/admin", headers=token_headers(3, "PATIENT")).status_code == 403
