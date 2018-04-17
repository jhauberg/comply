# coding=utf-8

import re

from comply.rules import Rule, RuleViolation, CheckFile
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
        if only_check_implementations:
            self.pattern = re.compile(FUNC_IMPL_PATTERN)

    MAX = 4

    pattern = re.compile(FUNC_BOTH_PATTERN)

    def augment(self, violation: RuleViolation):
        function_linenumber, function_line = violation.lines[0]

        # note that if we wanted to color up starting from the first exceeding parameter
        # we would have a hard time spanning the color over multiple lines, because
        # a reporter (e.g. 'human') may decide to clear colors per line
        # for now we just mark up the function name
        from_index, to_index = violation.meta['range']

        augmented_line = (function_line[:from_index] +
                          Colors.bad + function_line[from_index:to_index] + Colors.clear +
                          function_line[to_index:])

        violation.lines[0] = (function_linenumber, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        max_params = TooManyParams.MAX

        text = file.stripped

        from comply.util.stripping import strip_function_bodies

        # weed out potential false-positives by stripping the bodies of function implementations
        # outer most functions will remain as a collapsed body
        text_without_bodies = strip_function_bodies(text)

        for function_match in self.pattern.finditer(text_without_bodies):
            function_name = function_match.group('name')
            function_parameters = function_match.group('params')

            # naively splitting by comma (macros may cause trouble here)
            number_of_params = len(function_parameters.split(','))

            if number_of_params > max_params:
                offending_index = function_match.start()
                offending_line_number, offending_column = RuleViolation.at(offending_index,
                                                                           text)

                offending_lines = RuleViolation.lines_between(function_match.start(),
                                                              function_match.end(),
                                                              file.original)

                offender = self.violate(at=(offending_line_number, offending_column),
                                        lines=offending_lines,
                                        meta={'count': number_of_params,
                                              'max': max_params,
                                              'range': (offending_column - 1,
                                                        offending_column - 1 + len(function_name))})

                offenders.append(offender)

        return offenders
