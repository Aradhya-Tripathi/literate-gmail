import json
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleclient.utils import Json

with open("./settings.json") as f:
    settings = Json(json.loads(f.read()))

PARENT_PATH = settings["authentication_file_path"]
SCOPES = settings["scopes"]


def authenticate(credentials_path: str, token_path: str) -> dict:
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    creds = flow.run_local_server(
        port=0,
        success_message="Successfully Authenticate. You may close this window now.",
    )
    with open(token_path, "w") as token:
        token.write(creds.to_json())
    return creds.to_json()


def get_credentials(new_user: bool = False) -> Credentials:
    global PARENT_PATH
    if not PARENT_PATH:
        PARENT_PATH = input("Where do you want to store your tokens?: \n")
        edit_authentication_file_path(path=PARENT_PATH)
    credentials_path = os.path.join(PARENT_PATH, "credentials.json")
    token_path = os.path.join(PARENT_PATH, "token.json")

    def _new():
        if not os.path.exists(credentials_path):
            raise ValueError(
                f"Create a credentials file here {credentials_path} obtained from google oauth client setup"
            )
        return authenticate(credentials_path, token_path)

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


def edit_authentication_file_path(path: str):
    if not os.path.isabs(path):
        path = os.path.abspath(os.path.expanduser(path))
    settings["authentication_file_path"] = path
    settings.save()


def add_scope(scope):
    settings["scopes"].append(scope)
    settings.save()


def remove_scope(scope):
    scopes = settings["scopes"]
    if scope in scopes:
        scopes.remove(scope)

    settings["scopes"] = scopes
    settings.save()


def purge_tokens():
    path_to_creds = settings["authentication_file_path"]
    os.remove(os.path.join(path_to_creds, "token.json"))
