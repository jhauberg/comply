# coding=utf-8

from comply.rules.rule import *


class FileTooLong(Rule):
    """ Avoid exceeding 600 lines per source file.

    Files that are very long can be difficult to comprehend and may indicate that the complexity
    of the code is too high.
    """

    def __init__(self):
        Rule.__init__(self, name='file-too-long',
                      description='File is longer than recommended ({length} > {max} lines)',
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
