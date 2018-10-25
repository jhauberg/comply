# coding=utf-8

import re

from comply.rules.rule import *

from comply.printing import Colors


class PaddedParenthesis(Rule):
    """ Don't pad parenthesized groups with whitespace. """

    def __init__(self):
        Rule.__init__(self, name='padded-parens',
                      description='Opening or closing parenthesis padded with whitespace',
                      suggestion='Remove whitespace from the {left_or_right} side of the '
                                 'parenthesis.')

    pattern = re.compile(r'\(( +)\S|'  # opening paren with one or more whitespace up to any character, on the right
                         r'\S( +)\)')  # closing paren with one or more whitespace up to any character, to the left

    def augment_by_color(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range']
        length = to_index - from_index
        replacement = '~' * length

        augmented_line = (line[:from_index] +
                          Colors.BAD + replacement + Colors.RESET +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        for match in self.pattern.finditer(file.stripped):
            # get the matched group index
            # (because the pattern will only ever match for either group 1, or 2- never both)
            match_group_index = match.lastindex

            offending_index = match.start(match_group_index)
            offending_line_number, offending_column = file.line_number_at(offending_index)

            length = len(match.group(match_group_index))

            offending_range = (offending_column - 1,
                               offending_column - 1 + length)

            line = file.line_at(offending_line_number)

            right_group_index = 1

            left_or_right = 'right' if match_group_index == right_group_index else 'left'

            offender = self.violate(at=(offending_line_number, offending_column),
                                    lines=[(offending_line_number, line)],
                                    meta={'left_or_right': left_or_right,
                                          'range': offending_range})

            offenders.append(offender)

        return offenders

    @property
    def triggers(self):
        return [
            'func(↓ a, b, c)',
            'func(a, b, c↓ )',
            'func(↓  a, b, c↓ )'
        ]

    @property
    def nontriggers(self):
        return [
            'func(a, b, c)'
        ]
