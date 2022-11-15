import json
import threading
from concurrent.futures import ThreadPoolExecutor

from api import API
from utils import confirm

"""
Using Google's Client API is useless
it's shitty doesn't even complete suggestions wtf.
"""


class Gmail:
    def __init__(
        self, userId: str = "aradhyatripathi51@gmail.com", new_user: bool = False
    ) -> None:
        self.userId = userId
        self.service = self.resource(new_user=new_user)

    def resource(
        self, service: str = "gmail", version: str = "v1", new_user: bool = False
    ):
        return API(version=version, service=service, new_user=new_user)


class Messages(Gmail):
    def __init__(
        self, userId: str = "aradhyatripathi51@gmail.com", new_user: bool = False
    ) -> None:
        super().__init__(userId, new_user)

    def list(self, maxResults: int = 100):
        """
        Function representing users.messages.list
        """
        self.message_and_thread_ids = []
        self.messages = {}
        return self.service.messages(userId=self.userId).dispatch(
            method="get", params={"maxResults": maxResults}
        )

    def delete(self, message_id: str):
        """
        Function representing users.messages.delete
        """
        self.service.messages(userId=self.userId, resource=message_id).dispatch(
            method="delete"
        )

    def apply_filters(self, filters: dict) -> list:
        to_delete = []
        for message_from in self.messages:
            if filters.get("keyword").casefold() in message_from.casefold():
                to_delete.append(message_from)
        return to_delete

    def _apply_batch_delete_filters(self, message_ids):
        def _remove_from(message_id):
            return message_id[-15:]

        return list(map(_remove_from, message_ids))

    def save_deleted_messages(self, deleted_messages: dict, save_path: str):
        print(f"Writing {len(deleted_messages)} lines to {save_path}")
        with open(save_path, "w") as f:
            f.write(json.dumps(deleted_messages, indent=4))

    def batchDelete(
        self,
        filters: dict = {},
        save_deleted_messages: bool = True,
        deleted_message_path: str = "./deleted-messages.json",
        **kwargs,
    ):
        """
        Filters Supported Currently:
            {keyword: key}
        """
        to_delete = []
        self.scan_messages(**kwargs)
        if filters:
            to_delete = self.apply_filters(filters)
        else:
            to_delete.extend(list(self.messages.keys()))
            if not confirm(
                action=f"Are you sure you want to proceed with the deletion of {len(to_delete)} messages??? n/Y: "
            ):
                exit()
        if save_deleted_messages:
            to_delete_with_snippet = {}
            for detail in to_delete:
                if detail in self.messages:
                    to_delete_with_snippet[detail] = self.messages[detail]

            print(
                f"[MESSAGES] Writing {len(to_delete_with_snippet)} lines to {deleted_message_path}"
            )
            with open(deleted_message_path, "w") as dm:
                dm.write(json.dumps(to_delete_with_snippet, indent=4))

        to_delete = self._apply_batch_delete_filters(to_delete)

        self.service.messages(
            userId=self.userId,
            resource="batchDelete",
        ).dispatch(method="post", json=dict(ids=to_delete))

    def _scan_message_from_message_id(self, messages: dict):
        """
        Populates the self.messages dict in the format
        From-messageId: Snippet
        """
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

    def scan_messages(self, maxResults: int = 100):
        """
        Scan from and first 100 messages in users inbox.
        """
        self.lock = threading.Lock()
        mails = self.list(maxResults=maxResults)
        self.message_and_thread_ids.extend(mails["messages"])

        with ThreadPoolExecutor(max_workers=10) as exc:
            list(
                exc.map(self._scan_message_from_message_id, self.message_and_thread_ids)
            )


class Users(Gmail):
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
    # Messages().scan_messages(filters={"keyword": "github"})
    # Messages().batchDelete(save_deleted_messages=True, maxResults=100)
    Users().getProfile()
