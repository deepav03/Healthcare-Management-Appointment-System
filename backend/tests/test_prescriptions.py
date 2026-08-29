from conftest import token_headers


def prescription_payload():
    return {"patient_id": 1, "doctor_id": 1, "appointment_id": 1, "items": [{"medicine": "Demo Medicine", "dosage": "10 mg", "frequency": "Daily", "duration": "7 days", "instructions": "With water"}, {"medicine": "Demo Supplement", "dosage": "1 tablet", "frequency": "Daily", "duration": "5 days"}]}


def test_doctor_creates_prescription_with_items(business_client):
    response = business_client.post("/api/prescriptions", headers=token_headers(2, "DOCTOR"), json=prescription_payload())
    assert response.status_code == 201
    assert len(response.json()["items"]) == 2


def test_patient_can_view_own_prescription(business_client):
    business_client.post("/api/prescriptions", headers=token_headers(2, "DOCTOR"), json=prescription_payload())
    response = business_client.get("/api/prescriptions", headers=token_headers(3, "PATIENT"))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_duplicate_and_wrong_doctor_prescriptions_are_rejected(business_client):
    doctor = token_headers(2, "DOCTOR")
    business_client.post("/api/prescriptions", headers=doctor, json=prescription_payload())
    assert business_client.post("/api/prescriptions", headers=doctor, json=prescription_payload()).status_code == 409
    wrong = {**prescription_payload(), "doctor_id": 99}
    assert business_client.post("/api/prescriptions", headers=doctor, json=wrong).status_code == 403
