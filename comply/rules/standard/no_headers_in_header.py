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

    def augment(self, violation: RuleViolation):
        # assume only one offending line
        linenumber, line = violation.lines[0]

        violation.lines[0] = (linenumber, Colors.bad + line + Colors.clear)

    def collect(self, file: CheckFile):
        offenders = []

        if '.h' not in file.extension:
            return offenders

        text = file.original

        for inclusion in self.pattern.finditer(text):
            include_statement = inclusion.group(0)

            if ('<stdint.h>' in include_statement or '<inttypes.h>' in include_statement or
                    '<stdbool.h>' in include_statement):
                continue

            offending_index = inclusion.start()

            line, column = RuleViolation.at(offending_index, text, at_beginning=True)

            offending_line = (line, include_statement)

            offender = self.violate(at=(line, column),
                                    lines=[offending_line],
                                    meta={'inclusion': include_statement})

            offenders.append(offender)

            break

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE