# coding=utf-8

import re

from comply.rule import Rule, RuleViolation
from comply.util import truncated

from comply.rules.includes.pattern import INCLUDE_STMT_PATTERN


class IncludeGuard(Rule):
    def __init__(self):
        Rule.__init__(self, name='include-guard',
                      description='Header files should define an include guard to prevent double inclusion.',
                      suggestion='Wrap your header inside an include guard named "{0}".')

    def solution(self, offender: 'RuleViolation' =None):
        sol = super().solution(offender)

        symbol = offender.meta['guard'] if 'guard' in offender.meta.keys() else '???'

        return sol.format(symbol)

    def collect(self, text: str, filename: str, extension: str) -> list:
        offenders = []

        if '.h' not in extension:
            return offenders

        guard_name = filename.strip() + extension

        guard_name = guard_name.replace(' ', '_')
        guard_name = guard_name.replace('.', '_')

        # match include statements and capture suffixed content, if any
        pattern = r'^[\s\S]*#ifndef {0}\s*(?:\n|\r\n)\s*#define {0}[\s\S]*#endif\s*$'\
            .format(guard_name)

        match = re.match(pattern, text)

        if match is None:
            offender = self.violate(at=RuleViolation.where(text, 0),
                                    offending_text='',
                                    meta={'guard': guard_name})

            offenders.append(offender)

        return offenders
