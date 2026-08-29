from api.api_client import ApiClient


class BillingApi(ApiClient):
    def bills(self): return self.get("/api/bills")
    def create_bill(self, payload): return self.post("/api/bills", payload)
    def bill(self, bill_id): return self.get(f"/api/bills/{bill_id}")
