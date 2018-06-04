# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_IMPL_PATTERN


class TooManyFunctions(Rule):
    def __init__(self):
        Rule.__init__(self, name='too-many-funcs',
                      description='File might be too extensive ({count} > {max} functions)',
                      suggestion='Consider whether it might make sense for some functions to be split into separate files.')

    MAX = 7

    pattern = re.compile(FUNC_IMPL_PATTERN)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.collapsed

        matches = self.pattern.findall(text)

        max_matches = TooManyFunctions.MAX
        number_of_matches = len(matches)

        if number_of_matches > max_matches:
            offender = self.violate(at=file.line_number_at_top(),
                                    meta={'count': number_of_matches,
                                          'max': max_matches})

            offenders.append(offender)

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
