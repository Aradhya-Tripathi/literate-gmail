import json
import threading
from concurrent.futures import ThreadPoolExecutor

from api import API
from utils import confirm

"""
Using Google's Client API is useless
it's shitty doesn't even complete suggentions wtf.
"""


class GmailService:
    def __init__(
        self, userId: str = "aradhyatripathi51@gmail.com", new_user: bool = False
    ) -> None:
        self.userId = userId
        self.service = self.resource(new_user=new_user)

    def resource(
        self, service: str = "gmail", version: str = "v1", new_user: bool = False
    ):
        return API(version=version, service=service, new_user=new_user)


class Messages(GmailService):
    def __init__(
        self, userId: str = "aradhyatripathi51@gmail.com", new_user: bool = False
    ) -> None:
        super().__init__(userId, new_user)

    def message_list(self, maxResults: int = 100):
        self.message_and_thread_ids = []
        self.messages = {}
        return self.service.messages(userId=self.userId).dispatch(
            method="get", params={"maxResults": maxResults}
        )

    def delete(self, message_id: str):
        self.service.messages(userId=self.userId, resource=message_id).dispatch(
            method="delete"
        )

    def _apply_batchDelete_filters(self, filters: dict) -> list:
        to_delete = []
        for message_from in self.messages:
            message_id = message_from[-15:]
            if filters.get("keyword").casefold() in message_from.casefold():
                print(f"[DELETING] {message_from}")
                to_delete.append(message_id)
        return to_delete

    def batchDelete(self, filters: dict = {}, **kwargs):
        """
        Filters Supported Currently:
            {startswith_from: key}
        """
        to_delete = []
        self.scan_messages(**kwargs)
        if filters:
            to_delete = self._apply_batchDelete_filters(filters)
        else:
            for message in self.message_and_thread_ids:
                to_delete.append(message["id"])
            if not confirm(
                action=f"Are you sure you want to proceed with the deletion of {len(to_delete)} messages??? n/Y: "
            ):
                exit()
        self.service.messages(
            userId=self.userId,
            resource="batchDelete",
        ).dispatch(method="post", json=dict(ids=to_delete))

    def _scan_message_from_message_id(self, messages: dict):
        message_id = messages["id"]
        print("Working on: ", message_id)
        try:
            message = self.service.messages(
                userId=self.userId, resource=message_id
            ).dispatch(method="get")
            for index in message["payload"]["headers"]:
                if index["name"] == "From":
                    self.lock.acquire()
                    self.messages[f"{index['value']}-{message_id}"] = message["snippet"]
                    self.lock.release()
        except Exception as e:
            print(f"Message Id Errored Out: {message_id}\nException: {e}")

    def scan_messages(
        self,
        maxResults: int = 100,
        save: bool = True,
        save_path: str = "./messages.json",
    ):
        """
        Scan from and first 100 messages in users inbox.
        """
        self.lock = threading.Lock()
        mails = self.message_list(maxResults=maxResults)
        self.message_and_thread_ids.extend(mails["messages"])

        with ThreadPoolExecutor(max_workers=10) as exc:
            list(
                exc.map(self._scan_message_from_message_id, self.message_and_thread_ids)
            )

        if save:
            print(f"Writing {len(self.messages)} lines to {save_path}")
            with open(save_path, "w") as f:
                f.write(json.dumps(self.messages, indent=4))


class Users(GmailService):
    def __init__(
        self, userId: str = "aradhyatripathi51@gmail.com", new_user: bool = False
    ) -> None:
        super().__init__(userId, new_user)

    def getProfile(self):
        response = self.service.users(userId=self.userId, resource="profile").dispatch(
            method="get", params={"prettyPrint": True}
        )
        print(response)


if __name__ == "__main__":
    Messages().batchDelete(maxResults=100, save=True, filters={"keyword": "github"})
