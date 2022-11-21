import json
import os

import requests
from dotenv import load_dotenv

from googleclient.auth import get_credentials
from googleclient.utils import PrintWithModule

client = requests.Session()
print_with_module = PrintWithModule("API")
standard_params = {
    "alt": "json",
    "uploadType": None,
    "quotaUser": None,
    "fields": None,
    "callback": None,
    "upload_protocal": None,
    "access_token": None,
    "prettyPrint": True,
}
load_dotenv()


class GmailAPI:
    def __init__(
        self,
        version: str = "v1",
        authentication_type: str = "Bearer",
        always_json: bool = True,
        new_user: bool = False,
    ) -> None:
        """
        All these methods could be jammed into one method however in this case,
        method chaining seems more readable and usage. :)
        """
        # Since here we are using OAuth2.0 we need an access token on user's behalf
        # Since this Token is on users behalf we use the Bearer Token type.
        self.creds = (
            json.loads(get_credentials(new_user=new_user))
            if not os.getenv("CI")
            else {"token": "In-Test-Token"}
        )
        self.always_json = always_json
        self.client = client
        self.base_url = f"https://gmail.googleapis.com/gmail/{version}/"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"{authentication_type} {self.creds['token']}",
        }

    def users(self, userId: str, resource: str):
        self.current_request = self.base_url + f"users/{userId}/{resource}"
        return self

    def messages(self, userId: str, resource: str = None):
        """Defaults to constructing `users.messages.list` to send request to
        any other resource send in the resource argument"""
        resource = f"messages/{resource if resource else ''}"
        self.users(userId, resource=resource)
        return self

    def drafts(self, userId: str, resource: str = None):
        resource = f"drafts/{resource if resource else ''}"
        self.users(userId, resource=resource)
        return self

    def history(self, userId: str):
        resource = "history"
        self.users(userId, resource)
        return self

    def dispatch(
        self,
        method: str,
        data: dict = None,
        params: dict = None,
        json: dict = None,
        standard_params: dict = standard_params,
    ):
        def _send():
            response = self.client.send(request=prepared_request, timeout=5)
            if not response.ok:
                try:
                    reason = response.json()
                except requests.exceptions.JSONDecodeError:
                    reason = "Unknown"
                raise ValueError(
                    f"[API] Request failed response: {response.status_code}\nReason: {reason}"
                )
            if self.always_json:
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError:
                    print_with_module(
                        f"Retured no data with status code: {response.status_code}"
                    )
            return response

        if params:
            params.update(standard_params)
        else:
            params = standard_params

        request = requests.Request(
            method=method,
            url=self.current_request,
            headers=self.headers,
            json=json,
            params=params,
            data=data,
        )
        prepared_request = self.client.prepare_request(request=request)
        if os.getenv("CI"):
            return prepared_request
        return _send()
