# coding=utf-8

import sys

VERSION_PATTERN = r'^__version__ = [\'"]([^\'"]*)[\'"]'


def is_compatible() -> bool:
    if sys.version_info < (3, 5):
        return False

    return True
