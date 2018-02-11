# coding=utf-8

import re

from comply.rules import Rule, RuleViolation
from comply.rules.functions.pattern import FUNC_BOTH_PATTERN, FUNC_IMPL_PATTERN

from comply.printing import Colors


class TooManyParams(Rule):
    def __init__(self, only_check_implementations: bool=False):
        Rule.__init__(self, name='too-many-params',
                      description='Too many function parameters ({count} > {max})',
                      suggestion='This function may be taking on too much work. Consider refactoring.')

        # determine whether to only match implementations, or both prototypes and implementations
        # (prefer both, as e.g. inline functions won't be caught otherwise-
        # since they don't require a prototype, they may end up going unnoticed)
        self.only_checks_implementation = only_check_implementations

    MAX = 4

    def augment(self, violation: RuleViolation):
        function_linenumber, function_line = violation.lines[0]

        # note that if we wanted to color up starting from the first exceeding parameter
        # we would have a hard time spanning the color over multiple lines, because
        # a reporter (e.g. 'human') may decide to clear colors per line
        # for now we just mark up the function name
        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        augmented_line = (function_line[:from_index] +
                          Colors.bad + function_line[from_index:to_index] + Colors.clear +
                          function_line[to_index:])

        offending_lines = []

        for i, line in enumerate(augmented_line.splitlines()):
            offending_lines.append((function_linenumber + i, line))

        violation.lines = offending_lines

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        pattern = FUNC_IMPL_PATTERN if self.only_checks_implementation else FUNC_BOTH_PATTERN

        from comply.util.stripping import strip_function_bodies

        # weed out potential false-positives by stripping the bodies of function implementations
        # outer most functions will remain as a collapsed body
        text_without_bodies = strip_function_bodies(text)

        for function_match in re.finditer(pattern, text_without_bodies):
            function_name = function_match.group('name')
            function_parameters = function_match.group('params')
            function_result = function_match.group(0)

            function_linenumber, function_column = RuleViolation.where(text_without_bodies,
                                                                       function_match.start())

            max_params = TooManyParams.MAX
            number_of_params = len(function_parameters.split(','))

            if number_of_params > max_params:
                offender = self.violate(at=(function_linenumber, function_column),
                                        lines=[(function_linenumber, function_result)],
                                        meta={'count': number_of_params,
                                              'max': max_params,
                                              'range': (0, len(function_name))})

                offenders.append(offender)

        return offenders
