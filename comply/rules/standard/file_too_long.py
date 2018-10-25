# coding=utf-8

from comply.rules.rule import *


class FileTooLong(Rule):
    """ Avoid exceeding 600 lines per source file.

    Files that are very long can be difficult to navigate and easily comprehend, and may indicate
    that the file is too extensive and covering too many things.

    Note that, as with <tt>func-too-long</tt>, this limit is completely arbitrary and only serves
    as a general indicator of complexity. Whether or not a file is *actually* too long is highly
    variable and can only be judged on a situational basis.
    """

    def __init__(self):
        Rule.__init__(self, name='file-too-long',
                      description='File might be too complex ({length} > {max} lines)',
                      suggestion='Consider refactoring or splitting into separate files.')

    MAX = 600

    def collect(self, file: CheckFile):
        offenders = []

        max_length = FileTooLong.MAX

        length = file.original.count('\n')

        if length > max_length:
            offender = self.violate(at=file.line_number_at_top(),
                                    meta={'length': length,
                                          'max': max_length})

            offenders.append(offender)

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE

    @property
    def triggers(self):
        return [
            '▶' + make_filebody(FileTooLong.MAX + 1)
        ]

    @property
    def nontriggers(self):
        return [
            make_filebody(FileTooLong.MAX),
            make_filebody(FileTooLong.MAX - 1)
        ]


def make_filebody(number_of_lines: int) -> str:
    """ Return a string representing the contents of a file with a given number of lines.

        Only used for testing purposes.
    """

    body = ''

    for i in range(0, number_of_lines):
        body += '{n}/{c}: line\n'.format(n=i, c=number_of_lines)

    return body
