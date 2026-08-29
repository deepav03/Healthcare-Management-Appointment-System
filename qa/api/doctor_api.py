from api.api_client import ApiClient


class DoctorApi(ApiClient):
    def list(self, params=None): return self.get("/api/doctors", params)
    def get_doctor(self, doctor_id): return self.get(f"/api/doctors/{doctor_id}")
    def create(self, payload): return self.post("/api/doctors", payload)
    def update(self, doctor_id, payload): return self.patch(f"/api/doctors/{doctor_id}", payload)
