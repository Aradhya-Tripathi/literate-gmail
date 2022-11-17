import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path
from functools import lru_cache

SCOPES = ["https://mail.google.com/"]
PARENT_PATH = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = os.path.join(PARENT_PATH, "secure", "credentials.json")
TOKEN_PATH = os.path.join(PARENT_PATH, "secure", "token.json")


@lru_cache(maxsize=10)
def get_credentials(
    credentials_path: str = CREDENTIALS_PATH,
    token_path: str = TOKEN_PATH,
    new_user: bool = False,
) -> Credentials:
    def _new():
        if not os.path.exists(CREDENTIALS_PATH):
            raise ValueError(
                f"Create a credentials file here {CREDENTIALS_PATH} obtained from google oauth client setup"
            )
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