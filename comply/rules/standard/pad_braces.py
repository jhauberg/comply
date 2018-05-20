# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import KEYWORDS

from comply.printing import Colors


class PadBraces(Rule):
    def __init__(self):
        Rule.__init__(self, name='pad-braces',
                      description='Braced bodies should be padded with space on both sides',
                      suggestion='Add a single whitespace to the {left_or_right} of \'{brace}\'.')

    pattern = re.compile(r'[^\s]({)|'     # starting braces must always have whitespace to the left
                         r'(})[^\s;),]')  # ending braces have more options

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range']

        augmented_line = (line[:from_index] +
                          Colors.bad + line[from_index:to_index] + Colors.clear +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        for brace_match in self.pattern.finditer(text):
            brace_group_index = brace_match.lastindex

            offending_index = brace_match.start(brace_group_index)
            offending_line_number, offending_column = file.line_number_at(offending_index)

            length = brace_match.end() - brace_match.start()

            _, offending_range_column = file.line_number_at(brace_match.start())

            offending_range = (offending_range_column - 1,
                               offending_range_column - 1 + length)

            left_group_index = 1  # the first capture group; only one group will be matched

            left_or_right = 'left' if brace_group_index == left_group_index else 'right'

            brace = brace_match.group(brace_group_index)

            line = file.lines[offending_line_number - 1]

            offender = self.violate(at=(offending_line_number, offending_column),
                                    lines=[(offending_line_number, line)],
                                    meta={'left_or_right': left_or_right,
                                          'brace': brace,
                                          'range': offending_range})

            offenders.append(offender)

        return offenders
