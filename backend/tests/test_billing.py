from conftest import token_headers


def test_bill_calculation_and_patient_visibility(business_client):
    response = business_client.post("/api/bills", headers=token_headers(1, "ADMIN"), json={"patient_id": 1, "appointment_id": 1, "additional_charges": "20.00", "discount": "5.00", "tax": "11.50", "total_amount": "1.00"})
    assert response.status_code == 201
    assert response.json()["total_amount"] == "126.50"
    bills = business_client.get("/api/bills", headers=token_headers(3, "PATIENT"))
    assert bills.status_code == 200 and len(bills.json()) == 1


def test_duplicate_bill_and_invalid_amounts(business_client):
    payload = {"patient_id": 1, "appointment_id": 1, "additional_charges": 0, "discount": 0, "tax": 0}
    assert business_client.post("/api/bills", headers=token_headers(1, "ADMIN"), json=payload).status_code == 201
    assert business_client.post("/api/bills", headers=token_headers(1, "ADMIN"), json=payload).status_code == 409
    assert business_client.post("/api/bills", headers=token_headers(1, "ADMIN"), json={**payload, "appointment_id": 999}).status_code == 404
