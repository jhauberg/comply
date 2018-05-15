# coding=utf-8

import re

from comply.rules.rule import *

from comply.rules.patterns import INCLUDE_PATTERN, FUNC_PROT_PATTERN, FUNC_BODY_PATTERN


class NoUnifiedHeaders(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-unified-headers',
                      description='Avoid unified headers (headers whose only purpose is to include other headers)',
                      suggestion='Prefer forcing consumer to include each needed module.')

    pattern = re.compile(INCLUDE_PATTERN)

    def collect(self, file: CheckFile):
        offenders = []

        if '.h' not in file.extension:
            return offenders

        text = file.stripped

        has_includes = self.pattern.search(text) is not None

        if has_includes:
            has_function_prototypes = re.search(FUNC_PROT_PATTERN, text) is not None
            has_bodies = re.search(FUNC_BODY_PATTERN, text) is not None

            if not has_function_prototypes and not has_bodies:
                offender = self.violate(at=RuleViolation.at_top())
                offenders.append(offender)

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
