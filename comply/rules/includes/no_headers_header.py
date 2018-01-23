# coding=utf-8

import re

from comply.rule import Rule, RuleViolation

from comply.rules.includes.pattern import INCLUDE_STMT_PATTERN


class NoHeadersHeader(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-headers-header',
                      description='Header files should not include any other headers.',
                      suggestion='Replace "{0}" with a forward-declaration for each needed type.')

    def solution(self, offender: 'RuleViolation'=None):
        sol = super().solution(offender)

        inclusion = offender.meta['inclusion'] if 'inclusion' in offender.meta.keys() else '???'

        return sol.format(inclusion)

    def collect(self, text: str, filename: str, extension: str) -> list:
        offenders = []

        if '.h' not in extension:
            return offenders

        pattern = INCLUDE_STMT_PATTERN

        for inclusion in re.finditer(pattern, text):
            include_statement = inclusion.group(0)

            offender = self.violate(at=RuleViolation.where(text, inclusion.start()),
                                    offending_text=include_statement,
                                    meta={'inclusion': include_statement})

            offenders.append(offender)

        return offenders
