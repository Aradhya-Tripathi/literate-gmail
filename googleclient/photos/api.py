from googleclient.api import BaseAPI


class PhotosAPI(BaseAPI):
    def __init__(
        self,
        version: str = "v1",
        authentication_type: str = "Bearer",
        always_json: bool = True,
        new_user: bool = False,
    ):
        super().__init__(
            base_url="https://photoslibrary.googleapis.com/",
            version=version,
            authentication_type=authentication_type,
            always_json=always_json,
            new_user=new_user,
        )

    def albums(self, albumId: str = None, resource: str = None):
        self.current_request = (
            self.base_url
            + f"albums/{albumId if albumId else ''}{'/' + resource if resource else ''}"
        )
        return self
