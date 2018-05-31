# coding=utf-8

import re

from comply.rules.rule import *

from comply.util.truncation import truncated, Ellipsize

from comply.printing import Colors


class NoTodo(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-todo',
                      description='TODO: {todo}',
                      suggestion='Consider promoting this note to a full report in your issue tracker.')

    pattern = re.compile((r'(?:todo|fixme):'  # match notes in any combination of upper or lowercase
                          r'(.*)'),           # and everything until end of line
                         re.IGNORECASE)

    def collect(self, file: CheckFile):
        offenders = []

        for match in self.pattern.finditer(file.original):
            message = match.group(1)
            message = truncated(message.strip(),
                                length=60,
                                options=Ellipsize.options(at=Ellipsize.end))

            offender = self.violate_at_match(file, at=match)
            offender.meta = {'todo': message}

            offenders.append(offender)

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW
