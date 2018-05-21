# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import KEYWORDS

from comply.printing import Colors


class BraceStatementBodies(Rule):
    def __init__(self):
        Rule.__init__(self, name='brace-statement-bodies',
                      description='Always use braces for control statements',
                      suggestion='Add opening and ending braces for the statement body.')

    pattern = re.compile(r'\b({keywords})\b'.format(keywords=KEYWORDS))

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]
        column = violation.where[1]

        leading_space = ' ' * (column - 1)

        violation.lines = [
            (line_number, line + Colors.GOOD + ' {' + Colors.RESET),
            (line_number + 1, leading_space + '...'),
            (line_number + 2, leading_space + Colors.GOOD + '}' + Colors.RESET)
        ]

    def collect(self, file: CheckFile):
        offenders = []

        # first, strip anything inside parens; this will help us find dangling bodies
        from comply.util.stripping import strip_parens

        text = strip_parens(file.stripped)

        for dangling_match in self.pattern.finditer(text):
            # start from the ending of the control keyword
            # note that this procedure assumes all paren blocks have been stripped
            # e.g. `if (true) {` is expected as `if  {`
            ending = dangling_match.end()

            is_missing_opening_brace = True

            # move through the immediately following characters until finding a brace or
            # any other character (skipping whitespace and newlines)
            for c in text[ending:]:
                if c == '{':
                    # this body is properly braced
                    is_missing_opening_brace = False

                    break

                if c in [' ', '\r', '\n']:
                    # there can be any amount of whitespace or newline before the body
                    continue

                # any other character encountered; must mean that an opening brace is missing
                break

            if not is_missing_opening_brace:
                # move on to the next match
                continue

            offending_index = dangling_match.start()
            offending_line_number, offending_column = file.line_number_at(offending_index)

            lines = [(offending_line_number, file.lines[offending_line_number - 1])]

            offender = self.violate(at=(offending_line_number, offending_column),
                                    lines=lines)

            offenders.append(offender)

        return offenders
