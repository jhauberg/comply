# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.standard.list_needed_symbols import symbols_for_inclusion
from comply.rules.standard.no_headers_in_header import is_symbol_included_for_completeness
from comply.rules.patterns import INCLUDE_PATTERN

from comply.printing import Colors


class SymbolListedNotNeeded(Rule):
    """ Don't list unused symbols as needed.

    Helps in determining when a symbol is no longer used, potentially leading to being able to
    remove an inclusion completely, reducing dependencies and improving maintainability.

    See <tt>list-needed-symbols</tt>.
    """

    def __init__(self):
        Rule.__init__(self, name='symbol-listed-not-needed',
                      description='Unused symbol \'{symbol}\' is listed as needed',
                      suggestion='Remove symbol \'{symbol}\' from list.')

    pattern = re.compile(INCLUDE_PATTERN)

    def augment(self, violation: RuleViolation):
        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        # assume only one offending line
        linenumber, line = violation.lines[0]

        augmented_line = (line[:from_index] +
                          Colors.BAD + line[from_index:to_index] + Colors.RESET +
                          line[to_index:])

        violation.lines[0] = (linenumber, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.original

        for inclusion in self.pattern.finditer(text):
            symbols = symbols_for_inclusion(file, inclusion)

            if len(symbols) > 0:
                if '*' in symbols:
                    # a single star means everything will be matched; no violations can occur
                    continue

                for symbol in symbols:
                    symbol_type = symbol
                    sought_symbol = symbol

                    if is_symbol_included_for_completeness(symbol):
                        symbol_components = symbol.split(':')

                        symbol_type = symbol_components[0].strip()
                        sought_symbol = symbol_type

                    if not is_valid_symbol(sought_symbol):
                        continue

                    # search for symbol usage after include statement (in stripped body)
                    text_after_usage = file.stripped[inclusion.end():]

                    if not has_symbol_usage(sought_symbol, text_after_usage):
                        offending_index = text.index(symbol,
                                                     inclusion.start(),  # from the #include
                                                     text.index('\n', inclusion.end()))  # to end of line

                        linenumber, column = file.line_number_at(offending_index)

                        line = inclusion.group(0)

                        offending_line = (linenumber, line)

                        offender = self.violate(at=(linenumber, column),
                                                lines=[offending_line],
                                                meta={'symbol': symbol_type,
                                                      'range': (column - 1,
                                                                column - 1 + len(symbol))})

                        offenders.append(offender)

        return offenders

    @property
    def triggers(self):
        return [
            ('#include <header.h> // ↓mytype_t, ↓mytype_other_t\n'
             '...\n'
             'void func(...) {\n'
             '    ...\n'
             '}\n'
             '...')
        ]

    @property
    def nontriggers(self):
        return [
            ('#include <header.h> // mytype_t, mytype_other_t\n'
             '...\n'
             'void func(...) {\n'
             '    struct mytype_t a;\n'
             '    struct mytype_other_t b;\n'
             '}\n'
             '...')
        ]


def is_valid_symbol(symbol: str) -> bool:
    return ' ' not in symbol


def has_symbol_usage(symbol: str, text: str) -> bool:
    """ Determine whether a symbol occurs in a text. """

    # star matches any non-whitespace character
    symbol = symbol.replace('*', '\S*?')
    # match any use of symbol as a stand-alone element
    pattern = r'\b{0}\b'.format(symbol)

    # we're happy if just one match is found
    return True if (re.search(pattern, text) is not None) else False
