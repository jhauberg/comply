# coding=utf-8

import re

from comply.rules import Rule, RuleViolation, CheckFile
from comply.rules.functions.pattern import FUNC_BODY_PATTERN

from comply.util.scope import depth


class ScopeTooDeep(Rule):
    def __init__(self):
        Rule.__init__(self, name='scope-too-deep',
                      description='Scope is too deep ({depth} levels > {max})',
                      suggestion='Avoid nesting code too deeply. Consider refactoring.')

    MAX = 3

    pattern = re.compile(FUNC_BODY_PATTERN)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        lines = file.original.splitlines()

        max_depth = ScopeTooDeep.MAX

        for scope_match in self.pattern.finditer(text):
            scope_index = scope_match.start()
            scope_depth = depth(scope_index, text)

            if scope_depth > max_depth:
                line_number, column = RuleViolation.at(scope_index, text)

                offender = self.violate(at=(line_number, column),
                                        lines=[(line_number, lines[line_number - 1])],
                                        meta={'depth': scope_depth,
                                              'max': max_depth})

                offenders.append(offender)

        return offenders
