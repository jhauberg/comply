# coding=utf-8

import re

from comply.rules.rule import *

from comply.printing import Colors


class PadCommas(Rule):
    """ Always follow comma-separators by whitespace. """

    def __init__(self):
        Rule.__init__(self, name='pad-commas',
                      description='Comma separator is not followed by whitespace',
                      suggestion='Add a single whitespace or linebreak to the right of \',\'.')

    pattern = re.compile(r',[^\s]')  # any comma followed by non-whitespace

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range']

        augmented_line = (line[:from_index] +
                          Colors.BAD + line[from_index:to_index] + Colors.RESET +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        for comma_match in self.pattern.finditer(text):
            offending_index = comma_match.start()
            offending_line_number, offending_column = file.line_number_at(offending_index)

            length = comma_match.end() - comma_match.start()

            offending_range = (offending_column - 1,
                               offending_column - 1 + length)

            line = file.lines[offending_line_number - 1]

            offender = self.violate(at=(offending_line_number, offending_column),
                                    lines=[(offending_line_number, line)],
                                    meta={'range': offending_range})

            offenders.append(offender)

        return offenders
