# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_BODY_PATTERN

from comply.util.scope import depth


class ScopeTooDeep(Rule):
    def __init__(self):
        Rule.__init__(self, name='scope-too-deep',
                      description='Scope is too deep ({depth} > {max} levels)',
                      suggestion='Avoid nesting code too deeply. Consider refactoring.')

    MAX = 3

    pattern = re.compile(FUNC_BODY_PATTERN)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        max_depth = ScopeTooDeep.MAX

        for scope_match in self.pattern.finditer(text):
            scope_index = scope_match.start()
            scope_depth = depth(scope_index, text)

            if scope_depth > max_depth:
                line_number, column = file.line_number_at(scope_index, text)

                offender = self.violate(at=(line_number, column),
                                        lines=[(line_number, file.lines[line_number - 1])],
                                        meta={'depth': scope_depth,
                                              'max': max_depth})

                offenders.append(offender)

        return offenders
