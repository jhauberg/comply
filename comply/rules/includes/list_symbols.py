# coding=utf-8

import re

from comply.rule import Rule, RuleViolation
from comply.util import truncated

from comply.rules.includes.pattern import INCLUDE_STMT_PATTERN


class ListSymbols(Rule):
    def __init__(self):
        Rule.__init__(self, name='list-symbols',
                      description='Include statements should provide a list of the symbols they use.',
                      suggestion='Add a comment immediately after include statement, listing each used symbol. '
                                 'Example: "#include <header.h> // symb_t, symbols_*"')

    def violate(self, at: (int, int), offending_text: str, meta: dict=None) -> RuleViolation:
        if self.strips_violating_text:
            offending_text = offending_text.strip()

        what = '\'{0}\''.format(truncated(offending_text))

        return super().violate(at, what, meta)

    def collect(self, text: str, filename: str, extension: str) -> list:
        # match include statements and capture suffixed content, if any
        pattern = INCLUDE_STMT_PATTERN + r'(.*)'

        offenders = []

        for inclusion in re.finditer(pattern, text):
            suffix = inclusion.group(1)

            if not is_symbol_list(suffix):
                offender = self.violate(at=RuleViolation.where(text, inclusion.start()),
                                        offending_text=inclusion.group(0))

                offenders.append(offender)

        return offenders


def is_symbol_list(text: str) -> bool:
    """ Determine if a text looks like a symbol list. """

    text = text.strip()

    is_list_initiated = text.startswith('//')
    is_list = is_list_initiated and len(text) > 2

    return is_list
