# coding=utf-8

from comply.rules.rule import *

from comply.printing import Colors


class LineTooLong(Rule):
    def __init__(self):
        Rule.__init__(self, name='line-too-long',
                      description='Line is too long ({length} > {max})',
                      suggestion='Use shorter names or split statements to multiple lines.')

    MAX = 80

    def augment(self, violation: RuleViolation):
        # insert cursor to indicate max line length
        insertion_index = violation.meta['max']

        # assume only one offending line
        linenumber, line = violation.lines[0]

        breaker_line = (line[:insertion_index] + Colors.BAD + '|' +
                        line[insertion_index:] + Colors.RESET)

        violation.lines[0] = (linenumber, breaker_line)

    def collect(self, file: CheckFile):
        offenders = []

        max_characters = LineTooLong.MAX

        for i, line in enumerate(file.lines):
            length = len(line)

            if length <= max_characters:
                continue

            line_number = i + 1
            column = max_characters + 1

            offender = self.violate(at=(line_number, column),
                                    lines=[(line_number, line)])

            offender.meta = {'length': length,
                             'max': max_characters}

            offenders.append(offender)

        return offenders
