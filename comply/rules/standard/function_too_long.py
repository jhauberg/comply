# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_IMPL_PATTERN

from comply.util.scope import depth

from comply.printing import Colors


class FunctionTooLong(Rule):
    def __init__(self):
        Rule.__init__(self, name='func-too-long',
                      description='Function is too long ({length} > {max})',
                      suggestion='This function may be too complex. Consider refactoring.')

    MAX = 40

    pattern = re.compile(FUNC_IMPL_PATTERN)

    def augment(self, violation: RuleViolation):
        name = violation.meta['func'] if 'func' in violation.meta else '<unknown>'
        line_number = violation.meta['line'] if 'line' in violation.meta else 0

        # assume offending line is the second one
        breaker_linenumber, breaker_line = violation.lines[1]
        # add breaker just above offending line
        violation.lines.insert(1, (breaker_linenumber, '---'))

        for i, (linenumber, line) in enumerate(violation.lines):
            if i > 0:
                # mark breaker and everything below it
                violation.lines[i] = (linenumber, Colors.BAD + line + Colors.RESET)

        info_line = (Colors.EMPHASIS +
                     '(in {0}(..) starting at line {1})'.format(name, line_number) +
                     Colors.RESET)

        violation.lines.insert(0, (None, info_line))

    def collect(self, file: CheckFile):
        text = file.stripped

        offenders = []

        def check_func_body(body: str, name: str, line_number: int, starting_from_position: (int, int)):
            max_length = FunctionTooLong.MAX
            length = body.count('\n')

            if length > max_length:
                lines = body.splitlines()  # without newlines

                offending_line_index = max_length

                assert len(lines) > offending_line_index + 1

                actual_line_number = line_number - 1 + offending_line_index

                offending_lines = [
                    (actual_line_number, lines[offending_line_index - 1]),
                    (actual_line_number + 1, lines[offending_line_index]),
                    (actual_line_number + 2, lines[offending_line_index + 1])
                ]

                offender = self.violate(at=starting_from_position,
                                        lines=offending_lines,
                                        meta={'length': length,
                                              'max': max_length,
                                              'func': name,
                                              'line': starting_from_position[0]})

                offenders.append(offender)

        for function_match in self.pattern.finditer(text):
            func_body_start_index = function_match.end()  # we want to start before opening brace

            func_depth = depth(func_body_start_index, text)

            if func_depth == 0:
                offset = 1  # offset index by 1 to make sure we look one char ahead

                body_from_opening = text[func_body_start_index:]

                for c in body_from_opening:
                    # look for closing brace
                    if c == '}':
                        # note that we're assuming the indexing is offset 1 ahead so we can expect
                        # the depth function to look outside the body, as opposed to inside
                        func_inner_depth = depth(func_body_start_index + offset, text)

                        if func_inner_depth == 0:
                            line_number, column = file.line_number_at(func_body_start_index)

                            body = file.original[func_body_start_index:func_body_start_index + offset]

                            # we found end of body; now determine if it violates rule
                            check_func_body(body, function_match.group('name'), line_number,
                                            file.line_number_at(function_match.start(), span_entire_line=True))

                            break

                    offset += 1

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW
