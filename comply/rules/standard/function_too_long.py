# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_IMPL_PATTERN

from comply.util.scope import depth


class FunctionTooLong(Rule):
    """ Avoid exceeding 40 lines per function.

    A large function can be difficult to read and easily comprehend- especially so if it requires
    scrolling to fully fit on the viewers screen.

    Similar to <tt>too-many-params</tt>, when a function is getting large and increasingly complex,
    it is often a sign that it is doing too much and would likely benefit from being refactored
    into smaller parts.
    """

    def __init__(self):
        Rule.__init__(self, name='func-too-long',
                      description='Function is longer than recommended ({length} > {max} lines)',
                      suggestion='This function might be too complex. Consider refactoring.')

    MAX = 40

    pattern = re.compile(FUNC_IMPL_PATTERN)

    def collect(self, file: CheckFile):
        text = file.stripped

        offenders = []

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
                            body = file.original[func_body_start_index:
                                                 func_body_start_index + offset]

                            length = body.count('\n')
                            max_length = FunctionTooLong.MAX

                            if length > max_length:
                                start = function_match.start('name')
                                end = function_match.end('name')

                                offender = self.violate_at_character_range(
                                    file, starting=start, ending=end)

                                offender.meta = {
                                    'length': length,
                                    'max': max_length
                                }

                                offenders.append(offender)

                            break

                    offset += 1

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW

    @property
    def triggers(self):
        return [
            make_funcbody(FunctionTooLong.MAX + 1, expects_violation=True)
        ]

    @property
    def nontriggers(self):
        return [
            make_funcbody(FunctionTooLong.MAX),
            make_funcbody(FunctionTooLong.MAX - 1)
        ]


def make_funcbody(number_of_lines: int, expects_violation: bool=False) -> str:
    """ Return a string representing the contents of a function with a given number of lines.

        Only used for testing purposes.
    """

    body = 'void ↓func() {' if expects_violation else 'void func() {'

    for i in range(0, number_of_lines):
        body += '{n}/{c}: line\n'.format(n=i, c=number_of_lines)

    body += '}'

    return body
