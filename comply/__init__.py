# coding=utf-8

import sys
import os

VERSION_PATTERN = r'^__version__ = [\'"]([^\'"]*)[\'"]'


def is_compatible() -> bool:
    if sys.version_info < (3, 5):
        return False

    return True


def supports_unicode() -> bool:
    if os.name == 'nt':
        # disable unicode stuff when running on Windows
        # https://www.python.org/dev/peps/pep-0528/
        return False

    return True
