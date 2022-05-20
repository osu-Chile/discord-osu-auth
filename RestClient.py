from datetime import datetime, timedelta
import requests


class RestClient:

    def __init__(self, client_id: int, client_secret: str, auth_url: str, base_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.base_url = base_url
        self.token_expiration_date = datetime.now()
        self.token = None

    def get_auth_header(self):
        if (self.token is None or self.token == "") or (self.token_expiration_date < datetime.now()):
            self.token = self.get_token()

        return {"Authorization": f"Bearer {self.token}"}

    def get_token(self):
        request_data = {"client_id": {self.client_id},
                        "client_secret": {self.client_secret},
                        "grant_type": "client_credentials",
                        "scope": "public"}
        response = requests.post(self.auth_url, data=request_data)

        if not (200 <= response.status_code < 300):
            return None

        data = response.json()

        self.token_expiration_date = datetime.now() + timedelta(seconds=data["expires_in"] - 600)

        return data["access_token"]

    def get_user(self, user_id: int, mode: str = "osu"):
        return requests.get(f"{self.base_url}users/{user_id}/{mode}", headers=self.get_auth_header()).json()
