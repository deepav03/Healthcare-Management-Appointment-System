from conftest import token_headers


def test_admin_reports_and_filters(business_client):
    admin = token_headers(1, "ADMIN")
    appointments = business_client.get("/api/reports/appointments?status=COMPLETED", headers=admin)
    patients = business_client.get("/api/reports/patients", headers=admin)
    revenue = business_client.get("/api/reports/revenue", headers=admin)
    payments = business_client.get("/api/reports/payments", headers=admin)
    assert appointments.status_code == patients.status_code == revenue.status_code == payments.status_code == 200
    assert appointments.json()["data"][0]["status"] == "COMPLETED"
    assert len(patients.json()["data"]) == 1


def test_reports_are_admin_only(business_client):
    assert business_client.get("/api/reports/patients", headers=token_headers(3, "PATIENT")).status_code == 403
