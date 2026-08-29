from api.api_client import ApiClient


class ReportApi(ApiClient):
    def appointments(self, params=None): return self.get("/api/reports/appointments", params)
    def revenue(self, params=None): return self.get("/api/reports/revenue", params)
    def payments(self, params=None): return self.get("/api/reports/payments", params)
    def patients(self): return self.get("/api/reports/patients")
