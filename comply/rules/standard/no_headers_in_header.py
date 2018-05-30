# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN


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

        exceptions = ['<stdbool.h>',
                      '<stdint.h>',
                      '<inttypes.h>']

        for inclusion in self.pattern.finditer(file.stripped):
            include_statement = file.original[inclusion.start():inclusion.end()]

            found_exception = False

            for exception in exceptions:
                if exception in include_statement:
                    found_exception = True
                    break

            if found_exception:
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
