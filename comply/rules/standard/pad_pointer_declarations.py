# coding=utf-8

import re

from comply.rules.rule import *

from comply.printing import Colors


class PadPointerDeclarations(Rule):
    def __init__(self):
        Rule.__init__(self, name='pad-pointer-decls',
                      description='Pointer declarations should be padded with space on both sides',
                      suggestion='Add a single whitespace to the {left_or_right} of the asterisk.')

    pattern = re.compile(r'\*[^\s,*()=]|[^\s*()]\*')

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range']

        augmented_line = (line[:from_index] +
                          Colors.BAD + line[from_index:to_index] + Colors.RESET +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        for star_match in self.pattern.finditer(text):
            offending_index = star_match.start()

            is_probably_dereference = True

            index_left_of_star = offending_index + star_match.group().index('*') - 1

            for i in range(index_left_of_star, 0, -1):
                c = text[i]

                if c in [',', ';', '=', '!', '+', '-', '/', '(', ')', '[', ']', '\r', '\n']:
                    # found a character that signifies this is probably a dereferencing pointer
                    break
                else:
                    if c not in [' ', '\t']:
                        # found a character that signifies this is likely a declaration pointer
                        is_probably_dereference = False

                        break

            if not is_probably_dereference:
                offending_line_number, offending_column = file.line_number_at(offending_index)

                line = file.lines[offending_line_number - 1]

                length = star_match.end() - star_match.start()

                offending_range = (offending_column - 1, offending_column - 1 + length)
                offending_snippet = star_match.group()

                should_pad_right = offending_snippet.startswith('*')

                left_or_right = 'right' if should_pad_right else 'left'

                offender = self.violate(at=(offending_line_number, offending_column + (1 if not should_pad_right else 0)),
                                        lines=[(offending_line_number, line)],
                                        meta={'left_or_right': left_or_right,
                                              'range': offending_range})

                offenders.append(offender)

        return offenders
