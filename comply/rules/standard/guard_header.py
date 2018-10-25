# coding=utf-8

import re

from comply.rules.rule import *

from comply.printing import Colors


class GuardHeader(Rule):
    """ Always provide include guards in header files.

    Helps prevent redundant inclusions and improves compilation times.
    """

    def __init__(self):
        Rule.__init__(self, name='guard-header',
                      description='Header does not provide an include guard',
                      suggestion='Wrap your header in an include guard named "{guard}" or use "#pragma once".')

    def augment_by_color(self, violation: RuleViolation):
        guard = violation.meta['guard'] if 'guard' in violation.meta else '???'

        violation.lines = [
            (0, Colors.GOOD + '#ifndef {0}'.format(guard) + Colors.RESET),
            (1, Colors.GOOD + '#define {0}'.format(guard) + Colors.RESET),
            (2, '...'),
            (3, Colors.GOOD + '#endif' + Colors.RESET)
        ]

    def collect(self, file: CheckFile):
        if '.h' not in file.extension:
            return []

        offenders = []

        guard_name = file.filename.strip() + file.extension

        guard_name = guard_name.replace(' ', '_')
        guard_name = guard_name.replace('-', '_')
        guard_name = guard_name.replace('.', '_')

        pattern = re.compile((r'^(?:'
                              r'(\s*#ifndef {guard}\s*(?:\n|\r\n)'  # which is either an #ifndef
                              r'\s*#define {guard}\s*(?:\n|\r\n)'
                              r'[\s\S]*'
                              r'\s*#endif\s*$)'
                              r'|'
                              r'(\s*#pragma once))')  # or a #pragma once
                             .format(guard=guard_name))

        match = pattern.match(file.stripped)

        is_violation = True if match is None else False

        if is_violation:
            offender = self.violate(at=file.line_number_at_top(),
                                    meta={'guard': guard_name})

            offenders.append(offender)

        return offenders

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE

    @property
    def triggering_filename(self):
        return 'header.h'

    @property
    def triggers(self):
        return [
            ('▶// some header file\n'
             '...\n'
             '...'),
            ('▶// some header file\n'
             '...\n'
             '#pragma once'),
            ('▶// some header file\n'
             '...\n'
             '#ifndef header_h\n'
             '#define header_h\n'
             '...\n'
             '#endif'),
            ('▶// some header file\n'
             '#ifndef header_h\n'
             '#define header_h\n'
             '...\n'
             '#endif\n'
             '...\n'
             '...\n')
        ]

    @property
    def nontriggers(self):
        return [
            ('// some header file\n'
             '#pragma once\n'
             '...'),
            ('// some header file\n'
             '#ifndef header_h\n'
             '#define header_h\n'
             '...\n'
             '#endif')
        ]
