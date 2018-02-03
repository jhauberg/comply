# coding=utf-8

import sys
import os

# note that the order of stdout and stderr output is mixed up in PyCharm console
#  see https://youtrack.jetbrains.com/issue/IDEA-70016
# additionally, for reasoning behind diagnostic vs result:
#  see https://www.jstorimer.com/blogs/workingwithcode/7766119-when-to-use-stderr-instead-of-stdout

diagnostics = sys.stderr
results = sys.stdout


def printdiag(text: str, apply_prefix: bool=False, end: str=None):
    """ Print diagnostic output to the appropriate buffer.

        A diagnostic is output that is *not* directly related to the purpose of the program;
        for example: errors encountered during a run, or verbose informational messages.
    """

    diagnostic = 'comply: {0}'.format(text) if apply_prefix else text

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


class Colors:
    # https://stackoverflow.com/questions/287871/print-in-terminal-with-colors/21786287#21786287
    # https://askubuntu.com/questions/528928/how-to-do-underline-bold-italic-strikethrough-color-background-and-size-i

    strong = '\x1b[1m'
    emphasis = '\x1b[3m'
    underlined = '\x1b[4m'
    vague = '\x1b[0;37m'
    bad = '\x1b[0;31m'
    good = '\x1b[0;32m'
    warn = '\x1b[0;33m'
    clear = '\x1b[0m'

    @staticmethod
    def is_supported(buffer) -> bool:
        """ Determine whether an output buffer supports colored text. """

        if sys.platform == 'win32' or 'ANSICON' in os.environ:
            return False

        is_a_tty = buffer.isatty() and hasattr(buffer, 'isatty')

        if not is_a_tty:
            return False

        return True


if not Colors.is_supported(results):
    # note that we're assuming that diagnostics/stderr output is never colored
    Colors.strong = ''
    Colors.emphasis = ''
    Colors.underlined = ''
    Colors.vague = ''
    Colors.clear = ''
    Colors.bad = ''
    Colors.good = ''
    Colors.warn = ''
