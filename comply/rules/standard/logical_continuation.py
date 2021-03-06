# coding=utf-8

import re

from comply.rules.rule import *

from comply.printing import Colors


class LogicalContinuation(Rule):
    """ Don't begin lines with a logical continuation. """

    def __init__(self):
        Rule.__init__(self, name='logical-continuation',
                      description='Line begins with logical continuation',
                      suggestion='Move the logical continuation to the end of the previous line.')

    pattern = re.compile(r'\n\s*(&&|\|\|)')

    def augment_by_color(self, violation: RuleViolation):
        line_index = violation.index_of_starting_line()
        line_number, line = violation.lines[line_index]

        from_index, to_index = violation.meta['range']

        augmented_line = (line[:from_index] +
                          Colors.BAD + line[from_index:to_index] + Colors.RESET +
                          line[to_index:])

        violation.lines[line_index] = (line_number, augmented_line)

        if line_index > 0:
            operation = violation.meta['operation']

            line_index = line_index - 1
            line_number, line = violation.lines[line_index]

            augmented_line = line + ' ' + Colors.GOOD + operation + Colors.RESET

            violation.lines[line_index] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        for logical_match in self.pattern.finditer(text):
            offending_index = logical_match.start(1)

            offending_operation = logical_match.group(1)

            offending_line_number, offending_column = file.line_number_at(offending_index)

            offending_range = (offending_column - 1,
                               offending_column - 1 + len(offending_operation))

            offending_lines = file.lines_in_match(logical_match)

            offender = self.violate(at=(offending_line_number, offending_column),
                                    lines=offending_lines,
                                    meta={'range': offending_range,
                                          'operation': offending_operation})

            offenders.append(offender)

        return offenders

    @property
    def triggers(self):
        return [
            ('if (flag_a\n'
             ' ↓&& flag_b)'),
            ('if (flag_a\n'
             ' ↓|| flag_b)')
        ]

    @property
    def nontriggers(self):
        return [
            ('if (flag_a &&\n'
             '    flag_b)'),
            ('if (flag_a ||\n'
             '    flag_b)')
        ]
