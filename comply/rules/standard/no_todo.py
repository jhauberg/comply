# coding=utf-8

import re

from comply.rules.rule import *

from comply.util.truncation import truncated, Ellipsize

from comply.printing import Colors


class NoTodo(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-todo',
                      description='TODO: {todo}',
                      suggestion='Consider promoting this issue to a full report in your issue tracker.')

    pattern = re.compile(r'(TODO:|todo:)(.*)')

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range']

        augmented_line = (line[:from_index] +
                          Colors.BAD + line[from_index:to_index] + Colors.RESET +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        for match in self.pattern.finditer(file.original):
            line_number, column = file.line_number_at(match.start())

            line = file.lines[line_number - 1]

            message = match.group(2)
            message = truncated(message.strip(),
                                length=60,
                                options=Ellipsize.options(at=Ellipsize.end))

            column_end = column + len(match.group())

            offender = self.violate(at=(line_number, column),
                                    lines=[(line_number, line)],
                                    meta={'range': (column - 1, column_end),
                                          'todo': message})

            offenders.append(offender)

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW
