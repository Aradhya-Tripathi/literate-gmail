from unittest import TestCase

from googleclient.photos import Albums


class TestPhotos(TestCase):
    def test_albums(self):
        self.assertEqual(
            Albums().list().url,
            "https://photoslibrary.googleapis.com/v1/albums/?alt=json&prettyPrint=True",
        )
