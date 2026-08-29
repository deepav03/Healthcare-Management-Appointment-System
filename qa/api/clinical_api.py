from api.api_client import ApiClient


class ClinicalApi(ApiClient):
    def records(self): return self.get("/api/medical-records")
    def create_record(self, payload): return self.post("/api/medical-records", payload)
    def prescriptions(self): return self.get("/api/prescriptions")
    def create_prescription(self, payload): return self.post("/api/prescriptions", payload)
