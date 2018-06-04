# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN

from comply.rules.standard.list_needed_symbols import symbols_for_inclusion


class NoHeadersInHeader(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-headers-in-header',
                      description='Avoid including headers in header files',
                      suggestion='Replace \'{inclusion}\' with a forward-declaration for each needed type.')

    pattern = re.compile(INCLUDE_PATTERN)

    exceptions = ['stdbool.h',
                  'stdint.h',
                  'inttypes.h']

    def is_excepted(self, included_filename: str):
        allow_inclusion = False

        for exception in self.exceptions:
            if exception in included_filename:
                allow_inclusion = True

                break

        return allow_inclusion

    def is_inclusion_for_completeness(self, symbols: list) -> bool:
        if len(symbols) == 0:
            return False

        for symbol in symbols:
            if not is_symbol_included_for_completeness(symbol):
                return False

        return True

    def collect(self, file: CheckFile):
        offenders = []

        if '.h' not in file.extension:
            return offenders

        for inclusion in self.pattern.finditer(file.stripped):
            include_filename = file.original[inclusion.start('filename'):
                                             inclusion.end('filename')]

            if self.is_excepted(include_filename):
                continue

            symbols = symbols_for_inclusion(file, inclusion)

            if self.is_inclusion_for_completeness(symbols):
                continue

            include = file.original[inclusion.start():
                                    inclusion.end()]

            offender = self.violate_at_match(file, at=inclusion)
            offender.meta = {'inclusion': include}
            offenders.append(offender)

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW


def is_symbol_included_for_completeness(symbol: str) -> bool:
    """ Determine whether a symbol is listed for sake of type completeness. """

    return symbol.endswith(':completeness')
