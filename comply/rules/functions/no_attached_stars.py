# coding=utf-8

import re

from comply.rules import Rule, RuleViolation
from comply.rules.functions.pattern import FUNC_BOTH_PATTERN

from comply.printing import Colors


class NoAttachedStars(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-attached-stars',
                      description='Pointer stars should be padded with space on both sides',
                      suggestion='Add spacing to the {left_or_right} of the pointer star.')

    def augment(self, violation: RuleViolation):
        function_linenumber, function_line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        augmented_line = (function_line[:from_index] +
                          Colors.bad + function_line[from_index:to_index] + Colors.clear +
                          function_line[to_index:])

        leading_space = violation.meta['leading_space'] if 'leading_space' in violation.meta else 0

        violation.lines[0] = (function_linenumber, (' ' * leading_space) + augmented_line)

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        pattern = FUNC_BOTH_PATTERN

        from comply.util.stripping import strip_function_bodies

        # weed out potential false-positives by stripping the bodies of function implementations
        # outer most functions will remain as a collapsed body
        text_without_bodies = strip_function_bodies(text)

        for function_match in re.finditer(pattern, text_without_bodies):
            function_result = function_match.group()
            function_parameters = function_match.group('params')

            star_pattern = r'\*[^\s,*]|[^\s*]\*'

            for star_match in re.finditer(star_pattern, function_parameters):
                offending_index = function_match.start('params') + star_match.start()

                offending_line_number, offending_column = RuleViolation.at(offending_index,
                                                                           text_without_bodies)

                function_line_number, function_column = RuleViolation.at(function_match.start(),
                                                                         text_without_bodies)

                parameters_index_in_function_result = function_match.start('params') - function_match.start()

                offending_range = (parameters_index_in_function_result + star_match.start(),
                                   parameters_index_in_function_result + star_match.end())

                left_or_right = 'right' if star_match.group().startswith('*') else 'left'

                offender = self.violate(at=(offending_line_number, offending_column),
                                        lines=[(function_line_number, function_result)],
                                        meta={'leading_space': function_column - 1,
                                              'left_or_right': left_or_right,
                                              'range': offending_range})

                offenders.append(offender)

        return offenders
