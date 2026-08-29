import requests

from utils.config_reader import config
from utils.logger import get_logger


class ApiClient:
    def __init__(self, base_url=None, token=None, timeout=15):
        self.base_url = (base_url or config.api_base_url).rstrip('/')
        self.token = token
        self.timeout = timeout
        self.logger = get_logger(self.__class__.__name__)

    def headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def request(self, method, path, **kwargs):
        headers = {**self.headers(), **kwargs.pop("headers", {})}
        response = requests.request(method, f"{self.base_url}{path}", headers=headers, timeout=self.timeout, **kwargs)
        self.logger.info("%s %s -> %s", method, path, response.status_code)
        return response

    def get(self, path, params=None): return self.request("GET", path, params=params)
    def post(self, path, json=None): return self.request("POST", path, json=json)
    def patch(self, path, json=None): return self.request("PATCH", path, json=json)
    def delete(self, path): return self.request("DELETE", path)

    def login(self, email, password):
        response = self.post("/api/auth/login", {"email": email, "password": password})
        response.raise_for_status()
        self.token = response.json()["access_token"]
        return response
