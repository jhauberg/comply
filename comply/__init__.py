# coding=utf-8

import sys

from comply.printing import printdiag

VERSION_PATTERN = r'^__version__ = [\'"]([^\'"]*)[\'"]'

EXIT_CODE_SUCCESS = 0
EXIT_CODE_FAILURE = 1
EXIT_CODE_SUCCESS_WITH_SEVERE_VIOLATIONS = 2

PROFILING_IS_ENABLED = True


def is_compatible() -> bool:
    """ Determine whether the Python version is supported. """

    if sys.version_info < (3, 5):
        return False

    return True


def exit_if_not_compatible():
    """ Warn and exit if system is running unsupported Python version. """

    if not is_compatible():
        printdiag('Python 3.5 or newer required', as_error=True)

        sys.exit(EXIT_CODE_FAILURE)
