from api.api_client import ApiClient


class PatientApi(ApiClient):
    def list(self, params=None): return self.get("/api/patients", params)
    def me(self): return self.get("/api/patients/me")
    def get_patient(self, patient_id): return self.get(f"/api/patients/{patient_id}")
    def update(self, patient_id, payload): return self.patch(f"/api/patients/{patient_id}", payload)
