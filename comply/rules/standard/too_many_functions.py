# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_IMPL_PATTERN


class TooManyFunctions(Rule):
    def __init__(self):
        Rule.__init__(self, name='too-many-funcs',
                      description='Too many functions in a single file ({count} > {max})',
                      suggestion='Consider splitting into separate units.')

    MAX = 7

    pattern = re.compile(FUNC_IMPL_PATTERN)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        from comply.util.stripping import strip_function_bodies

        # weed out potential false-positives by stripping the bodies of function implementations
        # outer most functions will remain as a collapsed body
        text_without_bodies = strip_function_bodies(text)

        matches = self.pattern.findall(text_without_bodies)

        max_matches = TooManyFunctions.MAX
        number_of_matches = len(matches)

        if number_of_matches > max_matches:
            offender = self.violate(at=RuleViolation.at_top(),
                                    meta={'count': number_of_matches,
                                          'max': max_matches})

            offenders.append(offender)

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE