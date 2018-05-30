# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN

from comply.printing import Colors


class NoHeadersInHeader(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-headers-in-header',
                      description='Avoid including headers in header files',
                      suggestion='If possible, replace \'{inclusion}\' with a forward-declaration for each needed type.')

    pattern = re.compile(INCLUDE_PATTERN)

    def collect(self, file: CheckFile):
        offenders = []

        if '.h' not in file.extension:
            return offenders

        for inclusion in self.pattern.finditer(file.original):
            include_statement = inclusion.group(0)

            if ('<stdint.h>' in include_statement or '<inttypes.h>' in include_statement or
                    '<stdbool.h>' in include_statement):
                continue

            offender = self.violate_at_match(file, at=inclusion)
            offender.meta = {'inclusion': include_statement}
            offenders.append(offender)

            break

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
