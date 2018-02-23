# coding=utf-8

import re

from comply.rules import Rule, RuleViolation

from comply.rules.includes.pattern import INCLUDE_PATTERN
from comply.rules.functions.pattern import FUNC_PROT_PATTERN, FUNC_BODY_PATTERN


class AvoidUnifiedHeaders(Rule):
    def __init__(self):
        Rule.__init__(self, name='avoid-unified-headers',
                      description='Avoid unified (or umbrella) headers',
                      suggestion='Prefererererferererefsdf.')

    @property
    def severity(self):
        return RuleViolation.ALLOW

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        if '.h' not in extension:
            return offenders

        has_includes = re.search(INCLUDE_PATTERN, text) is not None

        if has_includes:
            has_function_prototypes = re.search(FUNC_PROT_PATTERN, text) is not None
            has_bodies = re.search(FUNC_BODY_PATTERN, text) is not None

            if not has_function_prototypes and not has_bodies:
                offender = self.violate(at=RuleViolation.at_top())

                offenders.append(offender)

        return offenders

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
