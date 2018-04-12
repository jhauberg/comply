# coding=utf-8

import re

from comply.rules import Rule, RuleViolation, CheckFile
from comply.rules.functions.pattern import FUNC_IMPL_PATTERN

from comply.printing import Colors


class SplitByName(Rule):
    def __init__(self):
        Rule.__init__(self, name='split-by-name',
                      description='Function names should be placed at the beginning of a line',
                      suggestion='Split function name and return type to separate lines.')

    pattern = re.compile(FUNC_IMPL_PATTERN)

    def augment(self, violation: RuleViolation):
        function_linenumber, function_line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        func_return = function_line[from_index:to_index]

        augmented_line = (function_line[:from_index] +
                          Colors.bad + func_return + Colors.clear +
                          function_line[to_index:])

        offending_lines = [
            (function_linenumber - 1, Colors.good + func_return + Colors.clear),
            (function_linenumber, augmented_line)
        ]

        violation.lines = offending_lines

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        lines = text.splitlines()

        from comply.util.stripping import strip_function_bodies

        # weed out potential false-positives by stripping the bodies of function implementations
        # outer most functions will remain as a collapsed body
        text_without_bodies = strip_function_bodies(text)

        for function_match in self.pattern.finditer(text_without_bodies):
            func_name = function_match.group('name')

            func_line_number, func_column = RuleViolation.at(function_match.start(),
                                                             text_without_bodies)
            func_line_index = func_line_number - 1

            line = lines[func_line_index]

            if not line.startswith(func_name):
                func_name_index = line.index(func_name)

                offender = self.violate(at=(func_line_number, func_column),
                                        lines=[(func_line_number, line)],
                                        meta={'range': (0, func_name_index)})

                offenders.append(offender)

        return offenders
