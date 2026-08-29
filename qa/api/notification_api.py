from api.api_client import ApiClient


class NotificationApi(ApiClient):
    def notifications(self): return self.get("/api/notifications")
    def read(self, notification_id): return self.patch(f"/api/notifications/{notification_id}/read")
    def read_all(self): return self.patch("/api/notifications/read-all")
