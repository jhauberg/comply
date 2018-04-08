# coding=utf-8

# coding=utf-8

import re

from comply.rules import Rule, RuleViolation
from comply.rules.functions.pattern import FUNC_PROT_PATTERN

from comply.printing import Colors


class NoRedundantConst(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-redundant-const',
                      description='Don\'t provide const qualifiers for parameter names in function prototypes',
                      suggestion='Remove const qualifier for parameter name.')

    def augment(self, violation: RuleViolation):
        function_linenumber, function_line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        augmented_line = (function_line[:from_index] +
                          Colors.bad + function_line[from_index:to_index] + Colors.clear +
                          function_line[to_index:])

        leading_space = violation.meta['leading_space'] if 'leading_space' in violation.meta else 0

        violation.lines[0] = (function_linenumber, (' ' * leading_space) + augmented_line)

    pattern = re.compile(FUNC_PROT_PATTERN)

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

                # take the last element; this should always be the right-most component
                # even if there's no stars in the parameter
                last_param_component = param_components[-1]

                if 'const' in last_param_component:
                    const_index = last_param_component.index('const')

                    has_pointer_degradation = ('[' in last_param_component and
                                               ']' in last_param_component)

                    if has_pointer_degradation:
                        # if the parameter is like "const arr[const]"
                        if last_param_component.count('const') > 1:
                            # then it's the last const that is the redundant one
                            const_index = last_param_component.rindex('const')
                        else:
                            # or has compounded parameter like
                            # 'enum suit const (* const suits)[2]'
                            compound_index = last_param_component.find(')')

                            is_compounded = (compound_index != -1 and
                                             compound_index < last_param_component.index('['))

                            if not is_compounded:
                                # ignore this const
                                const_index = -1

                    if const_index != -1:
                        up_to = len(param[:-len(last_param_component)]) + const_index

                        param_index_in_function_result = param_index - function_match.start()
                        const_index_in_function_result = param_index_in_function_result + up_to

                        offending_range = (const_index_in_function_result,
                                           const_index_in_function_result + len('const'))

                        offending_index = param_index + up_to
                        offending_line_number, offending_column = RuleViolation.at(offending_index,
                                                                                   text_without_bodies)

                        offender = self.violate(at=(offending_line_number, offending_column),
                                                lines=[(function_linenumber, function_result)],
                                                meta={'leading_space': function_column - 1,
                                                      'range': offending_range})

                        offenders.append(offender)

                param_index += len(param) + 1  # +1 to account for the split by ','

        return offenders
