# coding=utf-8

import re

from comply.rules import Rule, RuleViolation, CheckFile

from comply.util.truncation import truncated, Ellipsize

from comply.printing import Colors


class NoTodo(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-todo',
                      description='TODO: {todo}',
                      suggestion='Consider promoting this issue to a full report in your issue tracker.')

    pattern = re.compile(r'TODO:|todo:')

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        augmented_line = (line[:from_index] +
                          Colors.bad + line[from_index:to_index] + Colors.clear +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.original

        lines = text.splitlines()

        for match in self.pattern.finditer(text):
            line_number, column = RuleViolation.at(match.start(), text)

            column_end = column - 1 + (match.end() - match.start())

            line = lines[line_number - 1]

            message_start = column_end
            message = line[message_start:]
            message = truncated(message.strip(),
                                length=60,
                                options=Ellipsize.options(at=Ellipsize.end))

            offender = self.violate(at=(line_number, column),
                                    lines=[(line_number, line)],
                                    meta={'range': (column - 1, column_end),
                                          'todo': message})

            offenders.append(offender)

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW
