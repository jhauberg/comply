# coding=utf-8

import re

from comply.rules import Rule, RuleViolation

from comply.rules.includes.list_needed_symbols import is_symbol_list
from comply.rules.includes.pattern import INCLUDE_PATTERN

from comply.printing import Colors


class SymbolListedNotNeeded(Rule):
    def __init__(self):
        Rule.__init__(self, name='symbol-listed-not-needed',
                      description='Unused symbol \'{symbol}\' should not be listed as needed',
                      suggestion='Remove symbol \'{symbol}\' from list.',
                      expects_original_text=True)  # must use original text including comments

    def augment(self, violation: RuleViolation):
        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        # assume only one offending line
        linenumber, line = violation.lines[0]

        augmented_line = (line[:from_index] +
                          Colors.bad + line[from_index:to_index] + Colors.clear +
                          line[to_index:])

        violation.lines[0] = (linenumber, augmented_line)

    def collect(self, text: str, filename: str, extension: str):
        # match include statements and capture suffixed content, if any
        pattern = INCLUDE_PATTERN + r'(.*)'

        offenders = []

        for inclusion in re.finditer(pattern, text):
            suffix = inclusion.group(1).strip()

            if is_symbol_list(suffix):
                # assume comma-separated symbol list
                symbols_list = suffix[2:]
                symbols = [symbol.strip() for symbol in symbols_list.split(',')]

                if '*' in symbols:
                    # a single star means everything will be matched; no violations can occur
                    continue

                for symbol in symbols:
                    symbol_components = symbol.split(' as ')

                    symbol_type = symbol_components[0].strip()
                    sought_symbol = symbol_components[-1].strip()

                    # search for symbol usage after include statement
                    text_after_usage = text[inclusion.end():]

                    if not has_symbol_usage(sought_symbol, text_after_usage):
                        offending_index = text.index(symbol, inclusion.start(1), inclusion.end())

                        linenumber, column = RuleViolation.at(offending_index, text)

                        line = inclusion.group(0)

                        offending_line = (linenumber, line)

                        offender = self.violate(at=(linenumber, column),
                                                lines=[offending_line],
                                                meta={'symbol': symbol_type,
                                                      'range': (column - 1, column - 1 + len(symbol))})

                        offenders.append(offender)

        return offenders


def has_symbol_usage(symbol: str, text: str) -> bool:
    """ Determine whether a symbol occurs in a text. """

    # star matches any non-whitespace character
    symbol = symbol.replace('*', '\S*?')
    # match any use of symbol as a stand-alone element
    pattern = r'\b{0}\b'.format(symbol)

    # we're happy if just one match is found
    return True if (re.search(pattern, text) is not None) else False
