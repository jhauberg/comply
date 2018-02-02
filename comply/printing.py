# coding=utf-8

import sys

# note that the order of stdout and stderr output is mixed up in PyCharm console
#  see https://youtrack.jetbrains.com/issue/IDEA-70016
# additionally, for reasoning behind diagnostic vs result:
#  see https://www.jstorimer.com/blogs/workingwithcode/7766119-when-to-use-stderr-instead-of-stdout

diagnostics = sys.stderr
results = sys.stdout


def printdiag(text: str, apply_prefix: bool=True, end: str=None):
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


def supports_unicode() -> bool:

    required_encoding = 'UTF-8'

    if diagnostics.encoding != required_encoding or results.encoding != required_encoding:
        return False

    return True

