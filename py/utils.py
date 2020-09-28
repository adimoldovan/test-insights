SEPARATOR_LENGTH = 95


def print_banner(title):
    print()
    print("=" * SEPARATOR_LENGTH)
    print()
    print("{}{}".format(" " * int(((SEPARATOR_LENGTH - len(title)) / 2)), title))
    print()
    print("=" * SEPARATOR_LENGTH)
    print()


def print_separator():
    print("=" * SEPARATOR_LENGTH)
