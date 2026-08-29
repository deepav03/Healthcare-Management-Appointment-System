from api.api_client import ApiClient


class DashboardApi(ApiClient):
    def admin(self): return self.get("/api/dashboard/admin")
    def doctor(self): return self.get("/api/dashboard/doctor")
    def patient(self): return self.get("/api/dashboard/patient")
