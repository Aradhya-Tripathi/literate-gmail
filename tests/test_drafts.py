import os
from unittest import TestCase

from googleclient.gmail import Drafts

os.environ["CI"] = "1"


class TestDraft(TestCase):
    def test_list(self):
        prepared_request = Drafts().list()
        self.assertEqual(
            prepared_request.url,
            "https://gmail.googleapis.com/gmail/v1/users/me/drafts/?alt=json&prettyPrint=True",
        )

    def test_get(self):
        prepared_request = Drafts().get(id="random")
        self.assertEqual(
            prepared_request.url,
            "https://gmail.googleapis.com/gmail/v1/users/me/drafts/random?alt=json&prettyPrint=True",
        )

    def test_create(self):
        from email.message import Message

        message = Message()
        message["Body"] = "This is random"
        message["From"] = "1"
        message["To"] = "2"
        message["Subject"] = "Random"

        prepared_request = Drafts().create(message=message)
        self.assertEqual(
            prepared_request.url,
            "https://gmail.googleapis.com/gmail/v1/users/me/drafts/?alt=json&prettyPrint=True",
        )

        self.assertEqual(
            prepared_request.body.decode(),
            '{"message": {"raw": "Qm9keTogVGhpcyBpcyByYW5kb20KRnJvbTogMQpUbzogMgpTdWJqZWN0OiBSYW5kb20KCg=="}}',
        )

    def test_delete(self):
        prepared_request = Drafts().delete(id="random")
        self.assertEqual(
            prepared_request.url,
            "https://gmail.googleapis.com/gmail/v1/users/me/drafts/random?alt=json&prettyPrint=True",
        )
