import json
import threading
import typing
from concurrent.futures import ThreadPoolExecutor

from googleclient.gmail.api import GmailAPI
from googleclient.utils import (
    PrintWithModule,
    confirm,
    _apply_batch_delete_filters,
    apply_filters,
)

if typing.TYPE_CHECKING:
    from email.message import EmailMessage


print_with_module = PrintWithModule("GMAIL")


class Gmail:
    def __init__(
        self, userId: str = "aradhyatripathi51@gmail.com", new_user: bool = False
    ) -> None:
        self.userId = userId
        self.service = self.resource(new_user=new_user)

    def resource(self, version: str = "v1", new_user: bool = False):
        return GmailAPI(version=version, new_user=new_user)


class Messages(Gmail):
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

            print_with_module(
                f"Writing {len(to_delete_with_snippet)} lines to {deleted_message_path}"
            )
            with open(deleted_message_path, "w") as dm:
                dm.write(json.dumps(to_delete_with_snippet, indent=4))

        to_delete = _apply_batch_delete_filters(to_delete)

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
        self, maxResults: int = 100, multi_thread_config: dict = {"num_workers": 10}
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


class Drafts(Gmail):
    def _encode_draft_message(self, message: "EmailMessage"):
        import base64

        return base64.urlsafe_b64encode(message.as_string().encode()).decode()

    def createDraft(self, message: "EmailMessage"):
        encoded_message = self._encode_draft_message(message=message)
        return self.service.drafts(userId=self.userId).dispatch(
            method="post",
            json={"message": {"raw": encoded_message}},
        )

    def deleteDraft(self, id: str):
        self.service.drafts(userId=self.userId, resource=id).dispatch(method="delete")

    def getDraft(self, id: str):
        return self.service.drafts(userId=self.userId, resource=id).dispatch(
            method="get"
        )

    def listDraft(self):
        return self.service.drafts(userId=self.userId).dispatch(method="get")

    def sendDraft(self, id: str):
        return self.service.drafts(userId=self.userId, resource="send").dispatch(
            method="post", json=dict(id=id)
        )

    def updateDraft(self, id: str, message: "EmailMessage"):
        encoded_message = self._encode_draft_message(message=message)
        return self.service.drafts(userId=self.userId, resource=id).dispatch(
            method="put",
            json={"message": {"raw": encoded_message}},
        )


class History(Gmail):
    ...


class Users(Gmail):
    def getProfile(self):
        return self.service.users(userId=self.userId, resource="profile").dispatch(
            method="get", params={"prettyPrint": True}
        )
