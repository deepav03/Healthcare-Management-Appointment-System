from conftest import token_headers


def make_bill(client):
    response = client.post("/api/bills", headers=token_headers(1, "ADMIN"), json={"patient_id": 1, "appointment_id": 1, "tax": "10.00"})
    assert response.status_code == 201
    return response.json()


def test_successful_payment_updates_bill(business_client):
    bill = make_bill(business_client)
    response = business_client.post("/api/payments", headers=token_headers(3, "PATIENT"), json={"bill_id": bill["id"], "amount": "110.00", "payment_method": "CARD", "outcome": "SUCCESS"})
    assert response.status_code == 201
    assert response.json()["payment_status"] == "SUCCESS"
    assert business_client.get(f"/api/bills/{bill['id']}", headers=token_headers(3, "PATIENT")).json()["payment_status"] == "SUCCESS"


def test_failed_payment_is_deterministic_and_invalid_amount_rejected(business_client):
    bill = make_bill(business_client)
    failed = business_client.post("/api/payments", headers=token_headers(3, "PATIENT"), json={"bill_id": bill["id"], "amount": "110.00", "payment_method": "UPI", "outcome": "FAILED"})
    assert failed.status_code == 201 and failed.json()["payment_status"] == "FAILED"
    invalid = business_client.post("/api/payments", headers=token_headers(3, "PATIENT"), json={"bill_id": bill["id"], "amount": "1.00", "payment_method": "CASH", "outcome": "SUCCESS"})
    assert invalid.status_code == 400
