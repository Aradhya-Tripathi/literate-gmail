def confirm(action: str = None):
    choice = input(action)
    if choice == "y":
        go_ahead = True
    elif choice == "N":
        go_ahead = False
    else:
        confirm(action=action)

    return go_ahead
