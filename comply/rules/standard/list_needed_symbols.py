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

    pattern = re.compile(INCLUDE_PATTERN + r'(.*)')

    def augment(self, violation: RuleViolation):
        # assume only one offending line
        linenumber, line = violation.lines[0]

        violation.lines[0] = (linenumber,
                              line + Colors.good + ' // symbol_t, symbol_func_*' + Colors.clear)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.original

        for inclusion in self.pattern.finditer(text):
            suffix = inclusion.group(1)

            if not is_symbol_list(suffix):
                offending_index = inclusion.start()

                linenumber, column = file.line_number_at(offending_index, at_beginning=True)

                offending_line = (linenumber, inclusion.group(0))

                offender = self.violate(at=(linenumber, column),
                                        lines=[offending_line])

                offenders.append(offender)

        return offenders


def is_symbol_list(text: str) -> bool:
    """ Determine if a text looks like a symbol list. """

    text = text.strip()

    is_list_initiated = text.startswith('//')
    is_list = is_list_initiated and len(text) > 2

    return is_list
