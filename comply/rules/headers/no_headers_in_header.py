# coding=utf-8

import re

from comply.rules import Rule, RuleViolation

from comply.rules.includes.pattern import INCLUDE_PATTERN
from comply.printing import Colors


class NoHeadersInHeader(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-headers-in-header',
                      description='Header files should not include any other headers',
                      suggestion='Replace \'{inclusion}\' with a forward-declaration for each needed type.')

    def augment(self, violation: RuleViolation):
        # assume only one offending line
        linenumber, line = violation.lines[0]

        violation.lines[0] = (linenumber, Colors.bad + line + Colors.clear)

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        if '.h' not in extension:
            return offenders

        pattern = INCLUDE_PATTERN

        inclusion = re.search(pattern, text)

        if inclusion is not None:
            include_statement = inclusion.group(0)

            offending_index = inclusion.start()

            line, column = RuleViolation.where(text, offending_index, at_beginning=True)

            offending_line = (line, include_statement)

            offender = self.violate(at=(line, column),
                                    lines=[offending_line],
                                    meta={'inclusion': include_statement})

            offenders.append(offender)

        return offenders

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
