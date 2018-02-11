# coding=utf-8

import re

from comply.rules import Rule, RuleViolation

from comply.printing import Colors


class GuardHeader(Rule):
    def __init__(self):
        Rule.__init__(self, name='guard-header',
                      description='Header files should define an include guard to prevent double inclusion',
                      suggestion='Wrap your header inside an include guard named "{guard}".')

    def augment(self, violation: RuleViolation):
        guard = violation.meta['guard'] if 'guard' in violation.meta else '???'

        violation.lines = [
            (0, Colors.good + '#ifndef {0}'.format(guard) + Colors.clear),
            (1, Colors.good + '#define {0}'.format(guard) + Colors.clear),
            (2, '...'),
            (3, Colors.good + '#endif' + Colors.clear)
        ]

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        if '.h' not in extension:
            return offenders

        guard_name = filename.strip() + extension

        guard_name = guard_name.replace(' ', '_')
        guard_name = guard_name.replace('-', '_')
        guard_name = guard_name.replace('.', '_')

        pattern = r'^[\s\S]*#ifndef {0}\s*(?:\n|\r\n)\s*#define {0}[\s\S]*#endif\s*$'.format(
            guard_name)

        match = re.match(pattern, text)

        if match is None:
            offender = self.violate(at=RuleViolation.at_top(),
                                    meta={'guard': guard_name})

            offenders.append(offender)

        return offenders

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
