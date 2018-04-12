# coding=utf-8

import re

from comply.rules import Rule, RuleViolation, CheckFile

from comply.rules.includes.pattern import INCLUDE_PATTERN
from comply.rules.functions.pattern import FUNC_PROT_PATTERN, FUNC_BODY_PATTERN


class AvoidUnifiedHeaders(Rule):
    def __init__(self):
        Rule.__init__(self, name='avoid-unified-headers',
                      description='Avoid unified headers (headers whose only purpose is to include other headers)',
                      suggestion='Though convenient, unifying header inclusions does not promote loosely-coupled modules and potentially increases compile times.')

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
