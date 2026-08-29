from conftest import token_headers


def test_doctor_creates_and_updates_record(business_client):
    doctor = token_headers(2, "DOCTOR")
    response = business_client.post("/api/medical-records", headers=doctor, json={"patient_id": 1, "doctor_id": 1, "appointment_id": 1, "diagnosis": "Demo diagnosis"})
    assert response.status_code == 201
    record_id = response.json()["id"]
    assert business_client.patch(f"/api/medical-records/{record_id}", headers=doctor, json={"notes": "Updated"}).status_code == 200


def test_patient_views_own_record_but_not_other(business_client):
    doctor = token_headers(2, "DOCTOR")
    business_client.post("/api/medical-records", headers=doctor, json={"patient_id": 1, "doctor_id": 1, "appointment_id": 1, "diagnosis": "Demo"})
    patient = token_headers(3, "PATIENT")
    assert business_client.get("/api/medical-records", headers=patient).status_code == 200
    assert business_client.get("/api/patients/999/medical-records", headers=patient).status_code == 403


def test_record_requires_completed_matching_appointment(business_client):
    response = business_client.post("/api/medical-records", headers=token_headers(2, "DOCTOR"), json={"patient_id": 1, "doctor_id": 1, "appointment_id": 999})
    assert response.status_code == 400
