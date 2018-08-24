# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_BOTH_PATTERN, FUNC_IMPL_PATTERN

from comply.printing import Colors


class TooManyParams(Rule):
    """ Don't exceed 4 parameters per function.

    When a function has many parameters, it is often a sign that it is doing too much and would
    benefit from being refactored into smaller parts.

    Each parameter adds to the complexity of a function, and the more it has, the harder it becomes
    to understand (and use).
    <br/><br/>
    A common practice is to bundle parameters into a `struct` when many parameters are
    absolutely necessary (a pattern commonly referred to as *Parameter Object*).
    <br/><br/>
    This practice, however, does *not* reduce the complexity of the function-
    but it *does* improve its readability.

    References:

      * Stack Exchange discussion: [Are there guidelines on how many parameters a function should accept?](https://softwareengineering.stackexchange.com/a/145066)
    """

    def __init__(self, only_check_implementations: bool=False):
        Rule.__init__(self, name='too-many-params',
                      description='Function might be too broad ({count} > {max} parameters)',
                      suggestion='This function might be taking on too much work. Consider refactoring.')

        # determine whether to only match implementations, or both prototypes and implementations
        # (prefer both, as e.g. inline functions won't be caught otherwise-
        # since they don't require a prototype, they may end up going unnoticed)
        if only_check_implementations:
            self.pattern = re.compile(FUNC_IMPL_PATTERN)

    MAX = 4

    pattern = re.compile(FUNC_BOTH_PATTERN)

    def augment(self, violation: RuleViolation):
        line_index = violation.index_of_starting_line()

        function_line_number, function_line = violation.lines[line_index]

        # note that if we wanted to color up starting from the first exceeding parameter
        # we would have a hard time spanning the color over multiple lines, because
        # a reporter (e.g. 'human') may decide to clear colors per line
        # for now we just mark up the function name
        from_index, to_index = violation.meta['range']

        augmented_line = (function_line[:from_index] +
                          Colors.BAD + function_line[from_index:to_index] + Colors.RESET +
                          function_line[to_index:])

        violation.lines[line_index] = (function_line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        max_params = TooManyParams.MAX

        text = file.collapsed

        for function_match in self.pattern.finditer(text):
            function_name = function_match.group('name')
            function_parameters = function_match.group('params')

            # naively splitting by comma (macros may cause trouble here)
            number_of_params = len(function_parameters.split(','))

            if number_of_params > max_params:
                offending_index = function_match.start('name')
                offending_line_number, offending_column = file.line_number_at(offending_index)

                character_range = (function_match.start(),
                                   function_match.end())

                offending_lines = file.lines_in_character_range(character_range)

                offender = self.violate(at=(offending_line_number, offending_column),
                                        lines=offending_lines,
                                        meta={'count': number_of_params,
                                              'max': max_params,
                                              'range': (offending_column - 1,
                                                        offending_column - 1 + len(function_name))})

                offenders.append(offender)

        return offenders
