# coding=utf-8

import re

from comply.rules import Rule, RuleViolation

from comply.rules.includes.pattern import INCLUDE_STMT_PATTERN
from comply.printing import Colors


class ListNeededSymbols(Rule):
    def __init__(self):
        Rule.__init__(self, name='list-needed-symbols',
                      description='Include statements should indicate which symbols are needed',
                      suggestion='Add a comment immediately after include statement, listing each needed symbol.')

    def violate(self, at: (int, int), offending_lines: list=list(), meta: dict = None):
        # assume only one offending line
        linenumber, line = offending_lines[0]

        line = line + Colors.good + ' // symbol_t, symbol_func_*' + Colors.clear

        return super().violate(at, [(linenumber, line)], meta)

    def collect(self, text: str, filename: str, extension: str) -> list:
        # match include statements and capture suffixed content, if any
        pattern = INCLUDE_STMT_PATTERN + r'(.*)'

        offenders = []

        for inclusion in re.finditer(pattern, text):
            suffix = inclusion.group(1)

            if not is_symbol_list(suffix):
                offending_index = inclusion.start()

                linenumber, column = RuleViolation.where(text, offending_index, at_beginning=True)

                offending_line = (linenumber, inclusion.group(0))

                offender = self.violate(at=(linenumber, column),
                                        offending_lines=[offending_line])

                offenders.append(offender)

        return offenders


def is_symbol_list(text: str) -> bool:
    """ Determine if a text looks like a symbol list. """

    text = text.strip()

    is_list_initiated = text.startswith('//')
    is_list = is_list_initiated and len(text) > 2

    return is_list
