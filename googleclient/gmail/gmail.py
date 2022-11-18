import json
import os
import threading
import typing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from googleclient.gmail.api import GmailAPI
from googleclient.utils import (
    PrintWithModule,
    _apply_batch_delete_filters,
    apply_filters,
    confirm,
)

if typing.TYPE_CHECKING:
    from email.message import EmailMessage


print_with_module = PrintWithModule("GMAIL")


class Gmail:
    """
    Using 'me' as userId as it avoids domain-wide delegation errors.
    """

    def __init__(self, userId: str = "me", new_user: bool = False) -> None:
        self.userId = userId
        self.service = self.resource(new_user=new_user)

    def resource(self, version: str = "v1", new_user: bool = False):
        return GmailAPI(version=version, new_user=new_user)


class Messages(Gmail):
    def __init__(self, userId: str = "me", new_user: bool = False) -> None:
        super().__init__(userId, new_user)
        self.messages_path = os.path.join(
            Path(__file__).resolve().parent.parent.parent, "messages"
        )
        if not os.path.exists(self.messages_path):
            os.mkdir(self.messages_path)

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
        return self.service.messages(userId=self.userId, resource=message_id).dispatch(
            method="delete"
        )

    def batchDelete(
        self,
        filters: dict = {},
        message_ids: list = None,
        save_deleted_messages: bool = True,
        deleted_message_path: str = None,
        **kwargs,
    ):
        """
        Filters Supported Currently:
            {keyword: key}
        """
        to_delete = []
        if not message_ids:
            self.scan_messages(**kwargs)
            if filters:
                to_delete = apply_filters(self.messages, filters)
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

                deleted_message_path = (
                    deleted_message_path
                    if deleted_message_path
                    else os.path.join(self.messages_path, "deleted-messages.json")
                )

                print_with_module(
                    f"Writing {len(to_delete_with_snippet)} lines to {deleted_message_path}"
                )
                with open(deleted_message_path, "w") as dm:
                    dm.write(json.dumps(to_delete_with_snippet, indent=4))

            to_delete = _apply_batch_delete_filters(to_delete)
        else:
            to_delete = message_ids

        if to_delete:
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
        print_with_module("Working on: ", message_id)
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
            print_with_module(f"Message Id Errored Out: {message_id}\nException: {e}")

    def scan_messages(
        self,
        save_messages_path: str = None,
        maxResults: int = 100,
        multi_thread_config: dict = {"num_workers": 10},
    ):
        """
        Scan from and first 100 messages in users inbox.
        """
        self.lock = threading.Lock()
        mails = self.list(maxResults=maxResults)
        self.message_and_thread_ids.extend(mails["messages"])
        if multi_thread_config:
            with ThreadPoolExecutor(
                max_workers=multi_thread_config.get("num_workers")
            ) as exc:
                list(
                    exc.map(
                        self._scan_message_from_message_id, self.message_and_thread_ids
                    )
                )
        save_messages_path = (
            save_messages_path
            if save_messages_path
            else os.path.join(self.messages_path, "saved-messages.json")
        )
        with open(save_messages_path, "w") as sm:
            sm.write(json.dumps(self.messages, indent=4))


class Drafts(Gmail):
    def _encode_draft_message(self, message: "EmailMessage"):
        import base64

        return base64.urlsafe_b64encode(message.as_string().encode()).decode()

    def create(self, message: "EmailMessage"):
        encoded_message = self._encode_draft_message(message=message)
        return self.service.drafts(userId=self.userId).dispatch(
            method="post",
            json={"message": {"raw": encoded_message}},
        )

    def delete(self, id: str):
        return self.service.drafts(userId=self.userId, resource=id).dispatch(
            method="delete"
        )

    def get(self, id: str):
        return self.service.drafts(userId=self.userId, resource=id).dispatch(
            method="get"
        )

    def list(self):
        return self.service.drafts(userId=self.userId).dispatch(method="get")

    def send(self, id: str):
        return self.service.drafts(userId=self.userId, resource="send").dispatch(
            method="post", json=dict(id=id)
        )

    def update(self, id: str, message: "EmailMessage"):
        encoded_message = self._encode_draft_message(message=message)
        return self.service.drafts(userId=self.userId, resource=id).dispatch(
            method="put",
            json={"message": {"raw": encoded_message}},
        )


class History(Gmail):
    def list(self, **kwargs):
        return self.service.history(userId=self.userId).dispatch(method="get", **kwargs)


class Users(Gmail):
    def getProfile(self):
        return self.service.users(userId=self.userId, resource="profile").dispatch(
            method="get", params={"prettyPrint": True}
        )
