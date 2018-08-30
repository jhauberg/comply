# coding=utf-8

import re

from comply.rules.rule import *

from comply.util.truncation import truncated, Ellipsize


class NoTodo(Rule):
    """ Use `todo`'s liberally, but don't forget to deal with them.

    These small notes are great for quickly persisting thoughts directly related to
    specific parts of your code. They serve as reminders for both yourself, and others,
    that something needs to be looked at eventually.

    However, it is dangerous *todo-and-forget*; in time, these reminders may turn stale-
    the context might be forgotten, or the issue silently fixed- yet the `todo` remains.
    <br/><br/>
    This is a problem, because future-you may no longer understand why, or even *what*, is wrong.
    In such a case, you might not dare deleting it, rendering the `todo` as nothing but a source
    of confusion and obfuscation.
    """

    def __init__(self):
        Rule.__init__(self, name='no-todo',
                      description='TODO: {todo}',
                      suggestion='Consider promoting to a full report in your issue tracker.')

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

    @property
    def triggers(self):
        return [
            'source with a // ↓todo: find me',
            'source with a // ↓TODO: find me',
            'source           ↓todo: f'
        ]

    @property
    def nontriggers(self):
        return [
            'source with a // todo don\'t find me',
            'source with a // TODO don\'t find me',
            'source todo'
        ]
