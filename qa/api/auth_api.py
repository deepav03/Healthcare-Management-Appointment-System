from api.api_client import ApiClient


class AuthApi(ApiClient):
    def register(self, payload): return self.post("/api/auth/register", payload)
    def login_user(self, email, password): return self.login(email, password)
    def me(self): return self.get("/api/auth/me")
    def logout(self): return self.post("/api/auth/logout")
