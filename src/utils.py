import sys


def confirm(action: str = None):
    choice = input(action)
    go_ahead = False
    if choice == "y":
        go_ahead = True
    elif choice == "N":
        go_ahead = False
    else:
        confirm(action=action)

    return go_ahead


class PrintWithModule:
    def __init__(self, module):
        self.module = module

    def __call__(self, message: str):
        print(f"[{self.module}] {message}", file=sys.stderr)
