from googleclient.api import BaseAPI


class GmailAPI(BaseAPI):
    def __init__(
        self,
        version: str = "v1",
        authentication_type: str = "Bearer",
        always_json: bool = True,
        new_user: bool = False,
    ):
        super().__init__(
            base_url="https://gmail.googleapis.com/gmail/",
            version=version,
            authentication_type=authentication_type,
            always_json=always_json,
            new_user=new_user,
        )

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
