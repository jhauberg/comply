# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_PROT_PATTERN

from comply.printing import Colors


class NoRedundantConst(Rule):
    """ Don't mark parameter names as `const` in function prototypes.

    A function parameter name might be marked as `const` in its prototype, but implementations of
    the function are *not* required to comply with that- making it an implementation detail that
    should not be part of the exposed interface.
    """

    def __init__(self):
        Rule.__init__(self, name='no-redundant-const',
                      description='Parameter name marked const',
                      suggestion='Remove const qualifier for parameter name.')

    pattern = re.compile(FUNC_PROT_PATTERN)

    def augment(self, violation: RuleViolation):
        line_index = violation.index_of_starting_line()

        function_linenumber, function_line = violation.lines[line_index]

        from_index, to_index = violation.meta['range']

        augmented_line = (function_line[:from_index] +
                          Colors.BAD + function_line[from_index:to_index] + Colors.RESET +
                          function_line[to_index:])

        violation.lines[line_index] = (function_linenumber, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.collapsed

        for function_match in self.pattern.finditer(text):
            function_parameters = function_match.group('params')

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

                        offending_index = param_index + up_to
                        offending_line_number, offending_column = file.line_number_at(offending_index)

                        character_range = (function_match.start(),
                                           function_match.end())

                        offending_lines = file.lines_in_character_range(character_range)

                        offending_range = (offending_column - 1,
                                           offending_column - 1 + len('const'))

                        offender = self.violate(at=(offending_line_number, offending_column),
                                                lines=offending_lines,
                                                meta={'range': offending_range})

                        offenders.append(offender)

                param_index += len(param) + 1  # +1 to account for the split by ','

        return offenders
