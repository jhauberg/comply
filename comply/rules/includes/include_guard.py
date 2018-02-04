# coding=utf-8

import re

from comply.rules import Rule, RuleViolation


class IncludeGuard(Rule):
    def __init__(self):
        Rule.__init__(self, name='include-guard',
                      description='Header files should define an include guard to prevent double inclusion',
                      suggestion='Wrap your header inside an include guard named "{0}".')

    def solution(self, offender: 'RuleViolation'=None):
        sol = super().solution(offender)

        symbol = offender.meta['guard'] if 'guard' in offender.meta.keys() else '???'

        return sol.format(symbol)

    def collect(self, text: str, filename: str, extension: str) -> list:
        offenders = []

        if '.h' not in extension:
            return offenders

        guard_name = filename.strip() + extension

        guard_name = guard_name.replace(' ', '_')
        guard_name = guard_name.replace('-', '_')
        guard_name = guard_name.replace('.', '_')

        # match include statements and capture suffixed content, if any
        pattern = r'^[\s\S]*#ifndef {0}\s*(?:\n|\r\n)\s*#define {0}[\s\S]*#endif\s*$'\
            .format(guard_name)

        match = re.match(pattern, text)

        if match is None:
            line, column = RuleViolation.where(text, 0)

            offender = self.violate(at=(line, column),
                                    meta={'guard': guard_name})

            offenders.append(offender)

        return offenders

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
