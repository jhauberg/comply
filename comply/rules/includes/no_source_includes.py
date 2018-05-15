# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN

from comply.printing import Colors


class NoSourceIncludes(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-src-includes',
                      description='Don\' include source files',
                      suggestion='Remove #include directive.')

    pattern = re.compile(INCLUDE_PATTERN)

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        violation.lines[0] = (line_number, Colors.bad + line + Colors.clear)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.original  # todo: we actually *do* want comments stripped- just not literals

        for inclusion in self.pattern.finditer(text):
            include_stmt = inclusion.group()

            if include_stmt.endswith('.c'):
                offending_index = inclusion.start()

                line_number, column = RuleViolation.at(offending_index, text,
                                                       at_beginning=True)

                offending_line = (line_number, include_stmt)

                offender = self.violate(at=(line_number, column),
                                        lines=[offending_line])

                offenders.append(offender)

        return offenders
