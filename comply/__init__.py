# coding=utf-8

import sys

from comply.printing import printdiag

VERSION_PATTERN = r'^__version__ = [\'"]([^\'"]*)[\'"]'


def is_compatible() -> bool:
    if sys.version_info < (3, 5):
        return False

    return True


def exit_if_not_compatible():
    if not is_compatible():
        printdiag('Python 3.5 or newer required', as_error=True)

        sys.exit(1)
