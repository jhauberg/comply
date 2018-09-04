# coding=utf-8

"""
Provides functions and classes for printing diagnostics and colored output.
"""

import sys
import os

# note that the order of stdout and stderr output is mixed up in PyCharm console
#  see https://youtrack.jetbrains.com/issue/IDEA-70016
# additionally, for reasoning behind diagnostic vs result:
#  see https://www.jstorimer.com/blogs/workingwithcode/7766119-when-to-use-stderr-instead-of-stdout

diagnostics = sys.stderr
results = sys.stdout


def printdiag(text: str, as_error: bool=False, end: str=None):
    """ Print diagnostic output to the appropriate buffer.

        A diagnostic is output that is *not* directly related to the purpose of the program;
        for example: errors encountered during a run, or verbose informational messages.
    """

    diagnostic = 'comply: {0}'.format(text) if as_error else text

    if end is not None:
        print(diagnostic, file=diagnostics, end=end, flush=True)
    else:
        print(diagnostic, file=diagnostics, flush=True)


def printout(text: str):
    """ Print result output to the appropriate buffer.

        A result is any output that is directly related to the purpose of the program;
        in this case, any rule violations and accompanying solutions.
    """

    result = text

    print(result, file=results, flush=True)


def is_windows_environment() -> bool:
    """ Determine whether running on a Windows platform. """

    return os.name == 'nt'


def supports_unicode() -> bool:
    """ Determine whether the output buffers support unicode characters. """

    if is_windows_environment():
        # don't even try, just disable unicode stuff
        # https://www.python.org/dev/peps/pep-0528/
        return False

    required_encoding = 'UTF-8'

    if diagnostics.encoding != required_encoding or results.encoding != required_encoding:
        return False

    return True


def can_apply_colors() -> bool:
    """ Determine whether coloring can be applied to printouts. """

    return Colors.is_supported(results)


class Colors:
    """ Provides escape codes for commonly used colors. """

    # https://stackoverflow.com/questions/287871/print-in-terminal-with-colors/21786287#21786287
    # https://askubuntu.com/questions/528928/how-to-do-underline-bold-italic-strikethrough-color-background-and-size-i

    STRONG = '\x1b[1m'
    EMPHASIS = '\x1b[3m'
    UNDERLINED = '\x1b[4m'
    VAGUE = '\x1b[0;37m'
    DARK = '\x1b[0;90m'
    BAD = '\x1b[0;91m'
    GOOD = '\x1b[0;92m'
    WARN = '\x1b[0;33m'
    ALLOW = '\x1b[0;34m'
    DENY = '\x1b[0;31m'
    RESET = '\x1b[0m'

    @staticmethod
    def is_supported(buffer) -> bool:
        """ Determine whether an output buffer supports colored text. """

        # note: this is a dev and PyCharm-specific thing to support colors in the PyCharm console
        # (because isatty()/hasattr() will tell us no in this case)
        is_pycharm = 'PYCHARM' in os.environ

        is_a_tty = is_pycharm or (buffer.isatty() and hasattr(buffer, 'isatty'))

        if not is_a_tty:
            return False

        return True


if not can_apply_colors():
    # note that we're assuming that diagnostics/stderr output is never colored
    Colors.STRONG = ''
    Colors.EMPHASIS = ''
    Colors.UNDERLINED = ''
    Colors.VAGUE = ''
    Colors.DARK = ''
    Colors.RESET = ''
    Colors.BAD = ''
    Colors.GOOD = ''
    Colors.WARN = ''
    Colors.ALLOW = ''
    Colors.DENY = ''

if is_windows_environment():
    # enable color escape processing on Windows
    # see https://stackoverflow.com/a/36760881/144433
    import ctypes

    kernel32 = ctypes.windll.kernel32

    STD_OUTPUT_HANDLE = -11

    handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    ENABLE_PROCESSED_OUTPUT = 0x0001
    ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

    mode = (ENABLE_PROCESSED_OUTPUT |
            ENABLE_WRAP_AT_EOL_OUTPUT |
            ENABLE_VIRTUAL_TERMINAL_PROCESSING)

    kernel32.SetConsoleMode(handle, mode)
