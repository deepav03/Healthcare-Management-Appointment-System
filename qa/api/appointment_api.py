from api.api_client import ApiClient


class AppointmentApi(ApiClient):
    def create(self, payload): return self.post("/api/appointments", payload)
    def mine(self): return self.get("/api/appointments/my")
    def list(self, params=None): return self.get("/api/appointments", params)
    def get_appointment(self, appointment_id): return self.get(f"/api/appointments/{appointment_id}")
    def action(self, appointment_id, action): return self.patch(f"/api/appointments/{appointment_id}/{action}")
    def reschedule(self, appointment_id, payload): return self.patch(f"/api/appointments/{appointment_id}/reschedule", payload)
