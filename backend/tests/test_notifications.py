from conftest import token_headers


def test_notification_create_read_and_ownership(business_client):
    business_client.post("/api/bills", headers=token_headers(1, "ADMIN"), json={"patient_id": 1, "appointment_id": 1})
    notifications = business_client.get("/api/notifications", headers=token_headers(3, "PATIENT"))
    assert notifications.status_code == 200
    assert len(notifications.json()) == 1
    notification_id = notifications.json()[0]["id"]
    assert business_client.patch(f"/api/notifications/{notification_id}/read", headers=token_headers(3, "PATIENT")).json()["read_status"] is True
    assert business_client.patch(f"/api/notifications/{notification_id}/read", headers=token_headers(1, "ADMIN")).status_code == 403


def test_mark_all_read(business_client):
    business_client.post("/api/bills", headers=token_headers(1, "ADMIN"), json={"patient_id": 1, "appointment_id": 1})
    response = business_client.patch("/api/notifications/read-all", headers=token_headers(3, "PATIENT"))
    assert response.status_code == 200 and response.json()["updated"] == 1
