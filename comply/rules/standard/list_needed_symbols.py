# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN

from comply.printing import Colors


class ListNeededSymbols(Rule):
    def __init__(self):
        Rule.__init__(self, name='list-needed-symbols',
                      description='#include directives should indicate which symbols are needed',
                      suggestion='Add a comment listing each needed symbol immediately after the #include directive.')

    pattern = re.compile(INCLUDE_PATTERN)

    def augment(self, violation: RuleViolation):
        # assume only one offending line
        linenumber, line = violation.lines[0]

        violation.lines[0] = (linenumber,
                              line + Colors.GOOD + ' // symbol_t, symbol_func_*' + Colors.RESET)

    def collect(self, file: CheckFile):
        offenders = []

        for inclusion in self.pattern.finditer(file.stripped):
            symbols = symbols_for_inclusion(file, inclusion)

            if len(symbols) == 0:
                offender = self.violate_at_match(file, at=inclusion)
                offenders.append(offender)

        return offenders


def symbols_for_inclusion(file: CheckFile, match) -> list:
    """ Return a list of symbols for a match. """

    line_number, column = file.line_number_at(match.end())

    line = file.line_at(line_number)

    include_suffix = line[column:]

    if not is_symbol_list(include_suffix):
        return []

    listing = include_suffix[2:]  # everything except starting comment dashes ('//')

    return [symbol.strip() for symbol in listing.split(',')]


def is_symbol_list(text: str) -> bool:
    """ Determine whether a text looks like a list of symbols.

        e.g. '// symbol_t, another_symbol_t'.
    """

    text = text.strip()

    is_list_initiated = text.startswith('//')
    is_list = is_list_initiated and len(text) > 2

    return is_list
