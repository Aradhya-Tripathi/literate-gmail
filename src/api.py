import json

import requests

from auth import get_credentials
from utils import PrintWithModule

client = requests.Session()
print_with_module = PrintWithModule("API")


class API:
    def __init__(
        self,
        version: str = "v1",
        service: str = "gmail",
        authentication_type: str = "Bearer",
        always_json: bool = True,
        new_user: bool = False,
    ) -> None:
        # Since here we are using OAuth2.0 we need an access token on user's behalf
        # Since this Token is on users behalf we use the Bearer Token type.
        self.creds = json.loads(get_credentials(new_user=new_user))
        self.always_json = always_json
        self.client = client
        self.base_url = f"https://gmail.googleapis.com/{service}/{version}/"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"{authentication_type} {self.creds['token']}",
        }

    def messages(self, userId: str, resource: str = None):
        """Defaults to constructing `users.messages.list` to send request to
        any other resource send in the resource argument"""
        self.current_request = (
            self.base_url + f"users/{userId}/messages/{resource if resource else ''}"
        )
        return self

    def users(self, userId: str, resource: str):
        self.current_request = self.base_url + f"users/{userId}/{resource}"
        return self

    def dispatch(
        self,
        method: str,
        data: dict = None,
        params: dict = None,
        json: str = None,
    ):
        method = getattr(self.client, method)
        response = method(
            url=self.current_request,
            data=data,
            json=json,
            params=params,
            headers=self.headers,
        )
        if not response.ok:
            raise ValueError(
                f"[API] Request failed response: {response.status_code}\nReason: {response.json()}"
            )
        if self.always_json:
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                print_with_module(
                    f"Retured no data with status code: {response.status_code}"
                )
        return response
