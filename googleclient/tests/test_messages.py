from unittest import TestCase

from googleclient.gmail import Messages, Users


class TestMessages(TestCase):
    def test_user_profile(self):
        request_object = Users().getProfile()
        self.assertEqual(
            request_object.url,
            "https://gmail.googleapis.com/gmail/v1/users/me/profile?prettyPrint=True&alt=json",
        )

    def test_list(self):
        request_object = Messages().list(maxResults=2)
        self.assertEqual(
            request_object.url,
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/?maxResults=2&alt=json&prettyPrint=True",
        )

        request_object = Messages().list()
        self.assertEqual(
            request_object.url,
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/?maxResults=100&alt=json&prettyPrint=True",
        )

    def test_delete(self):
        request_object = Messages().delete(message_id="message_id")
        self.assertEqual(
            request_object.url,
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/message_id?alt=json&prettyPrint=True",
        )
