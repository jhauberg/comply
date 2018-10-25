# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN

from comply.rules.standard.require_symbols import symbols_for_inclusion


class HeaderInHeader(Rule):
    """ Don't include other headers if you can avoid it.

    Avoiding header inclusions can help keep compile times low.

    Forcing source files to include everything they need helps provide a clear picture on
    the dependencies of the particular unit and makes it easier to spot redundancies.

    References:

      * Our Machinery: [Physical Design](http://ourmachinery.com/post/physical-design)
      * Rob Pike: [Notes on Programming in C](http://www.lysator.liu.se/c/pikestyle.html)
      * Malcolm Inglis: [c-style](https://github.com/mcinglis/c-style#include-the-definition-of-everything-you-use)
    """

    def __init__(self):
        Rule.__init__(self, name='header-in-header',
                      description='Header included in header',
                      suggestion='Replace \'{inclusion}\' with a forward-declaration for each '
                                 'needed type.')

    pattern = re.compile(INCLUDE_PATTERN)

    exceptions = ['stdbool.h',
                  'stdint.h',
                  'stddef.h',
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
        if '.h' not in file.extension:
            return []

        offenders = []

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

    @property
    def triggering_filename(self):
        return 'header.h'

    @property
    def triggers(self):
        return [
            ('// some header file\n'
             '↓#include <header.h>'),
            ('// some header file\n'
             '↓#include <header.h> // type')
        ]

    @property
    def nontriggers(self):
        return [
            ('#include <stdbool.h>\n'
             '#include <stdint.h>\n'
             '#include <inttypes.h>'),
            ('// some header file\n'
             'struct symbol_t;'),
            '#include <header.h> // type :completeness',
            '#include <header.h> // type:completeness'
        ]


def is_symbol_included_for_completeness(symbol: str) -> bool:
    """ Determine whether a symbol is listed for sake of type completeness. """

    return symbol.endswith(':completeness')
