from api.api_client import ApiClient


class ScheduleApi(ApiClient):
    def list(self, doctor_id): return self.get(f"/api/doctors/{doctor_id}/schedules")
    def create(self, doctor_id, payload): return self.post(f"/api/doctors/{doctor_id}/schedules", payload)
    def update(self, schedule_id, payload): return self.patch(f"/api/schedules/{schedule_id}", payload)
    def delete_schedule(self, schedule_id): return self.delete(f"/api/schedules/{schedule_id}")
    def availability(self, doctor_id, date): return self.get(f"/api/doctors/{doctor_id}/availability/{date}")
