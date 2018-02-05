# coding=utf-8

import re

from comply.rules import Rule, RuleViolation

from comply.rules.includes.pattern import INCLUDE_STMT_PATTERN
from comply.printing import Colors


class NoHeadersHeader(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-headers-header',
                      description='Header files should not include any other headers',
                      suggestion='Replace \'{0}\' with a forward-declaration for each needed type.')

    def solution(self, violation: RuleViolation=None):
        inclusion = violation.meta['inclusion'] if 'inclusion' in violation.meta.keys() else '???'

        return super().solution(violation).format(inclusion)

    def augment(self, violation: RuleViolation):
        # assume only one offending line
        linenumber, line = violation.lines[0]

        violation.lines[0] = (linenumber, Colors.bad + line + Colors.clear)

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        if '.h' not in extension:
            return offenders

        pattern = INCLUDE_STMT_PATTERN

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
