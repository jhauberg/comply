# coding=utf-8

import re

from comply.rule import Rule, RuleOffender
from comply.util import truncated, Ellipsize

from comply.rules.includes.require_symbols import is_symbol_list


class UnusedSymbol(Rule):
    def __init__(self):
        Rule.__init__(self, name='unused-symbol',
                      description='Unused symbols should not be listed as required.',
                      suggestion='Remove symbol \'{0}\' from list.')

    def offend(self, at: (int, int), offending_text: str, token: str=None) -> RuleOffender:
        which = self
        where = at

        what = '\'{0}\' in \'{1}\'' \
            .format(token, truncated(offending_text, ellipsize=Ellipsize.start))

        return RuleOffender(which, where, what, token)

    def collect(self, text: str) -> list:
        # match include statements and capture suffixed content, if any
        pattern = r'#include\s+[<"].+?[>"](.*)'

        offenders = []

        for inclusion in re.finditer(pattern, text):
            suffix = inclusion.group(1).strip()

            if is_symbol_list(suffix):
                # assume comma-separated symbol list
                symbols_list = suffix[2:]
                symbols = [symbol.strip() for symbol in symbols_list.split(',')]

                for symbol in symbols:
                    # search for symbol usage after include statement
                    text_after_usage = text[inclusion.end():]

                    if not has_symbol_usage(symbol, text_after_usage):
                        offender = self.offend(at=RuleOffender.where(text, inclusion.start()),
                                               offending_text=inclusion.group(0),
                                               token=symbol)

                        offenders.append(offender)

        return offenders


def has_symbol_usage(symbol: str, text: str) -> bool:
    # star matches any non-whitespace character
    symbol = symbol.replace('*', '\S*?')
    # match any use of symbol as a stand-alone element
    pattern = r'\b{0}\b'.format(symbol)

    # we're happy if just one match is found
    return True if (re.search(pattern, text) is not None) else False
