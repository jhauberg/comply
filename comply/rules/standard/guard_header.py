# coding=utf-8

import re

from comply.rules.rule import *

from comply.printing import Colors


class GuardHeader(Rule):
    def __init__(self):
        Rule.__init__(self, name='guard-header',
                      description='Header files should provide an include guard to prevent double inclusion',
                      suggestion='Wrap your header in an include guard named "{guard}" or use "#pragma once".')

    def augment(self, violation: RuleViolation):
        guard = violation.meta['guard'] if 'guard' in violation.meta else '???'

        violation.lines = [
            (0, Colors.good + '#ifndef {0}'.format(guard) + Colors.clear),
            (1, Colors.good + '#define {0}'.format(guard) + Colors.clear),
            (2, '...'),
            (3, Colors.good + '#endif' + Colors.clear)
        ]

    def collect(self, file: CheckFile):
        offenders = []

        if '.h' not in file.extension:
            return offenders

        if '#pragma once' in file.stripped:
            return offenders

        guard_name = file.filename.strip() + file.extension

        guard_name = guard_name.replace(' ', '_')
        guard_name = guard_name.replace('-', '_')
        guard_name = guard_name.replace('.', '_')

        pattern = re.compile(
            r'^[\s\S]*#ifndef {guard}\s*(?:\n|\r\n)\s*#define {guard}[\s\S]*#endif\s*$'.format(
                guard=guard_name))

        text = file.stripped

        match = pattern.match(text)

        if match is None:
            offender = self.violate(at=RuleViolation.at_top(),
                                    meta={'guard': guard_name})

            offenders.append(offender)

        return offenders

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
