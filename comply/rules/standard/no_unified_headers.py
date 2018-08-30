# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN, FUNC_PROT_PATTERN, FUNC_BODY_PATTERN


class NoUnifiedHeaders(Rule):
    """ Don't use unified headers if you can avoid it.

    A unified header is a header file whose only purpose is to include other header files.

    As convenient as they may be, unified headers do not promote modularity and increases
    compile time in cases where the consumer does not need all of the included headers.

    References:

      * Malcolm Inglis: [c-style](https://github.com/mcinglis/c-style#avoid-unified-headers)
    """

    def __init__(self):
        Rule.__init__(self, name='no-unified-headers',
                      description='Avoid unified headers',
                      suggestion='Prefer individually including each needed header.')

    pattern = re.compile(INCLUDE_PATTERN)

    def collect(self, file: CheckFile):
        if '.h' not in file.extension:
            return []

        offenders = []

        text = file.stripped

        has_includes = self.pattern.search(text) is not None

        if has_includes:
            has_function_prototypes = re.search(FUNC_PROT_PATTERN, text) is not None
            has_bodies = re.search(FUNC_BODY_PATTERN, text) is not None

            if not has_function_prototypes and not has_bodies:
                offender = self.violate_at_file(file)
                offenders.append(offender)

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW

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
             '#include <header.h>\n'
             '#include "other_header.h"')
        ]

    @property
    def nontriggers(self):
        return [
            ('// some header file\n'
             '#include <header.h>\n'
             '#include "other_header.h"'
             'void proto_func(int a);')
        ]
