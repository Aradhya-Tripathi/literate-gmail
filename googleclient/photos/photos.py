from googleclient.photos.api import PhotosAPI


class Photos:
    def __init__(self, new_user: bool = False):
        self.service = self.build(new_user=new_user)

    def build(self, version: str = "v1", new_user: bool = False):
        return PhotosAPI(version=version, new_user=new_user)


class Albums(Photos):
    def create(
        self,
        title: str,
        albumId: str = None,
        productUrl: str = None,
        isWriteable: bool = None,
        shareInfo: dict = None,
        mediaItemsCount: str = None,
        coverPhotoBaseUrl: str = None,
        coverPhotoMediaItemId: str = None,
    ):
        metadata = {
            "id": albumId,
            "title": title,
            "productUrl": productUrl,
            "isWriteable": isWriteable,
            "shareInfo": shareInfo,
            "mediaItemsCount": mediaItemsCount,
            "coverPhotoBaseUrl": coverPhotoBaseUrl,
            "coverPhotoMediaItemId": coverPhotoMediaItemId,
        }

        return self.service.albums().dispatch(
            method="post",
            json={"album": metadata},
        )

    def get(self, albumId: str):
        return self.service.albums(albumId=albumId).dispatch(method="get")

    def list(self, **params):
        return self.service.albums().dispatch(method="get", params=params)
