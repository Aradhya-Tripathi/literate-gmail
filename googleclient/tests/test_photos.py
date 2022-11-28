from googleclient.tests import BaseTestClass

from googleclient.photos import Albums


class TestPhotos(BaseTestClass):
    def test_albums(self):
        self.assertEqual(
            Albums().list().url,
            "https://photoslibrary.googleapis.com/v1/albums/?alt=json&prettyPrint=True",
        )
