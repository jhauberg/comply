# coding=utf-8

import re

from comply.rules import Rule, RuleViolation

from comply.printing import Colors


class NoAttachedStars(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-attached-stars',
                      description='Pointer stars should be padded with space on both sides',
                      suggestion='Add spacing to the {left_or_right} of the pointer star.')

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        augmented_line = (line[:from_index] +
                          Colors.bad + line[from_index:to_index] + Colors.clear +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        lines = text.splitlines()

        from comply.util.stripping import strip_literals

        text_without_literals = strip_literals(text)

        star_pattern = r'\*[^\s,*()=]|[^\s*()]\*'

        for star_match in re.finditer(star_pattern, text_without_literals):
            offending_index = star_match.start()

            is_probably_dereference = True

            index_left_of_star = offending_index + star_match.group().index('*') - 1

            for i in range(index_left_of_star, 0, -1):
                c = text_without_literals[i]

                if c in [',', '=', '!', '+', '-', '/', '(', ')', '[', ']', '\r', '\n']:
                    # found a character that signifies this is probably a dereferencing pointer
                    break
                else:
                    if c not in [' ', '\t']:
                        # found a character that signifies this is likely a declaration pointer
                        is_probably_dereference = False

                        break

            if not is_probably_dereference:
                offending_line_number, offending_column = RuleViolation.at(offending_index,
                                                                           text_without_literals)

                line = lines[offending_line_number - 1]

                length = star_match.end() - star_match.start()

                offending_range = (offending_column - 1, offending_column - 1 + length)
                offending_snippet = star_match.group()

                left_or_right = 'right' if offending_snippet.startswith('*') else 'left'

                offender = self.violate(at=(offending_line_number, offending_column),
                                        lines=[(offending_line_number, line)],
                                        meta={'left_or_right': left_or_right,
                                              'range': offending_range})

                offenders.append(offender)

        return offenders
