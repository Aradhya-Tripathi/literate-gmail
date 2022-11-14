import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from functools import lru_cache

SCOPES = ["https://mail.google.com/"]


@lru_cache(maxsize=10)
def get_credentials(
    credentials_path: str = "./credentials.json",
    token_path: str = "./src/token.json",
    new_user: bool = False,
) -> Credentials:
    def _new():
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write((creds.to_json()))
        return creds.to_json()

    if new_user:
        return _new()

    try:
        creds = Credentials.from_authorized_user_file(token_path)
        if creds.expired:
            raise ValueError("Credentials Expired")
        return creds.to_json()
    except (FileNotFoundError, ValueError):
        if not os.path.exists(credentials_path):
            raise ValueError(f"Expected a credentials file here {credentials_path}")
        return _new()
