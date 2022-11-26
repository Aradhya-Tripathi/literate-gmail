import sys
import json


class Json(dict):
    def save(self):
        with open("./settings.json", "w") as f:
            f.write(json.dumps(self, indent=2))


def confirm(action: str = None):
    choice = input(action).lower()
    go_ahead = False
    if choice == "y":
        go_ahead = True
    elif choice == "n":
        go_ahead = False
    else:
        confirm(action=action)

    return go_ahead


def _apply_batch_delete_filters(message_ids):
    def _remove_from(message_id):
        return message_id[-15:]

    return list(map(_remove_from, message_ids))


def apply_filters(messages: dict, filters: dict) -> list:
    to_delete = []
    for message_from in messages:
        if filters.get("keyword").casefold() in message_from.casefold():
            to_delete.append(message_from)
    return to_delete


class PrintWithModule:
    def __init__(self, module):
        self.module = module

    def __call__(self, *args):
        if args:
            try:
                args = " ".join(args)
                print(f"[{self.module}] {args}", file=sys.stderr)
            except TypeError:
                print(f"[{self.module}] {args[0]}", file=sys.stderr)
