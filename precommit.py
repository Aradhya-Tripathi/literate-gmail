import json

from googleclient.utils import Json

with open("./settings.json") as f:
    settings = Json(json.loads(f.read()))

if settings["authentication_file_path"]:
    settings["authentication_file_path"] = ""
    settings.save()
