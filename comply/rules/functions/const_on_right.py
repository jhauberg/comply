# coding=utf-8

import re

from comply.rules import Rule, RuleViolation
from comply.rules.functions.pattern import FUNC_BOTH_PATTERN

from comply.printing import Colors


class ConstOnRight(Rule):
    def __init__(self):
        Rule.__init__(self, name='const-on-right',
                      description='Prefer const qualifiers on the right',
                      suggestion='Place const qualifier to the right of the type declaration.')

    def augment(self, violation: RuleViolation):
        function_linenumber, function_line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)
        insert_index = violation.meta['insert'] if 'insert' in violation.meta else 0

        char_at_insertion = function_line[insert_index]
        # determine whether the 'const' should be right-padded
        add_padding = char_at_insertion not in [')', ',']

        # insert proper placement first, assuming this index always occur later
        augmented_line = (function_line[:insert_index] +
                          Colors.good + 'const' + (' ' if add_padding else '') + Colors.clear +
                          function_line[insert_index:])

        # then markup part to delete (again, assuming that these indices are before insertion index)
        augmented_line = (augmented_line[:from_index] +
                          Colors.bad + augmented_line[from_index:to_index] + Colors.clear +
                          augmented_line[to_index:])

        leading_space = violation.meta['leading_space'] if 'leading_space' in violation.meta else 0

        violation.lines[0] = (function_linenumber, (' ' * leading_space) + augmented_line)

    pattern = re.compile(FUNC_BOTH_PATTERN)

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        from comply.util.stripping import strip_function_bodies

        # weed out potential false-positives by stripping the bodies of function implementations
        # outer most functions will remain as a collapsed body
        text_without_bodies = strip_function_bodies(text)

        for function_match in self.pattern.finditer(text_without_bodies):
            function_parameters = function_match.group('params')
            function_result = function_match.group()

            function_linenumber, function_column = RuleViolation.at(function_match.start(),
                                                                    text_without_bodies)

            param_index = function_match.start('params')

            # naively splitting by comma (macros may cause trouble here)
            params = function_parameters.split(',')

            for param in params:
                param_components = param.split('*')

                param_component_index = 0

                exclude_last_component = param.count('*') > 0

                iterable_components = (param_components if not exclude_last_component else
                                       param_components[:-1])

                for param_component in iterable_components:
                    param_component_stripped = param_component.strip()

                    has_const_on_left = param_component_stripped.startswith('const')
                    is_array_pointer = '[' in param_component and ']' in param_component
                    is_by_itself = len(param_component_stripped.split(' ')) == 1

                    if has_const_on_left and not is_by_itself and not is_array_pointer:
                        up_to = param_component_index + param_component.index('const')

                        param_index_in_function_result = param_index - function_match.start()
                        const_index_in_function_result = param_index_in_function_result + up_to

                        offending_range = (const_index_in_function_result,
                                           const_index_in_function_result + len('const'))

                        offending_index = param_index + up_to
                        offending_line_number, offending_column = RuleViolation.at(offending_index,
                                                                                   text_without_bodies)

                        insertion_index = param_index_in_function_result + len(param_component)

                        offender = self.violate(at=(offending_line_number, offending_column),
                                                lines=[(function_linenumber, function_result)],
                                                meta={'leading_space': function_column - 1,
                                                      'range': offending_range,
                                                      'insert': insertion_index})

                        offenders.append(offender)

                    param_component_index += len(param_component) + 1  # +1 to account for '*'

                param_index += len(param) + 1  # +1 to account for the split by ','

        return offenders
