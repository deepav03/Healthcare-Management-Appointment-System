from api.api_client import ApiClient


class PaymentApi(ApiClient):
    def payments(self): return self.get("/api/payments")
    def create_payment(self, payload): return self.post("/api/payments", payload)
    def payment(self, payment_id): return self.get(f"/api/payments/{payment_id}")
