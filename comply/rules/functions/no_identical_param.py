# coding=utf-8

import re

from comply.rules import Rule, RuleViolation
from comply.rules.functions.pattern import FUNC_PROT_PATTERN

from comply.printing import Colors


class NoIdenticalParam(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-identical-param',
                      description='Parameter \'{0}\' should not be named identically to its type \'{1}\'',
                      suggestion='Rename parameter \'{0}\' to something meaningful or omit it.')

    def reason(self, violation: RuleViolation=None):
        parameter_name = violation.meta['param'] if 'param' in violation.meta else 0
        parameter_type = violation.meta['type'] if 'type' in violation.meta else 0

        return super().reason(violation).format(parameter_name, parameter_type)

    def solution(self, violation: RuleViolation=None):
        parameter_name = violation.meta['param'] if 'param' in violation.meta else 0

        return super().solution(violation).format(parameter_name)

    def augment(self, violation: RuleViolation):
        function_linenumber, function_line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        augmented_line = (function_line[:from_index] +
                          Colors.bad + function_line[from_index:to_index] + Colors.clear +
                          function_line[to_index:])

        # todo: this seems like a common pattern for functions which may span multiple lines; refactor into util or similar
        offending_lines = []

        for i, line in enumerate(augmented_line.splitlines()):
            offending_lines.append((function_linenumber + i, line))

        violation.lines = offending_lines

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        pattern = FUNC_PROT_PATTERN

        from comply.util.stripping import strip_function_bodies

        # weed out potential false-positives by stripping the bodies of function implementations
        text_without_bodies = strip_function_bodies(text)

        for function_match in re.finditer(pattern, text_without_bodies):
            function_parameters = function_match.group('params')

            # naively split by comma; won't yield correct results in all cases,
            # but it doesn't need to for the following logic to work out
            separated_parameters = list(re.finditer(r'(.*?)(,|$)', function_parameters))

            for func_param in separated_parameters:
                param = func_param.group(1)
                # matches any word component in a parameter (that isn't 'const')
                type_components = list(re.finditer(r'(?!const\b)\b\w[^\s]*\b', param))

                if len(type_components) > 1:  # must be more than two word components in the param
                    func_param_name = type_components[-1]  # last or right-most component
                    func_param_types = type_components[:-1]

                    types = [x.group() for x in func_param_types]

                    if func_param_name.group() in types:
                        param_start = func_param.start(1) + func_param_name.start()
                        param_end = func_param.end(1)

                        offending_index = (function_match.start('params') +
                                           param_start)

                        function_linenumber, function_column = RuleViolation.where(text_without_bodies,
                                                                                   offending_index)

                        params_start_index = function_match.start('params') - function_match.start()

                        function_result = function_match.group(0)

                        param_type = ' '.join(types)

                        offender = self.violate(at=(function_linenumber, function_column),
                                                lines=[(function_linenumber, function_result)],
                                                meta={'param': func_param_name.group(),
                                                      'type': param_type,
                                                      'range': (params_start_index + param_start,
                                                                params_start_index + param_end)})

                        offenders.append(offender)

        return offenders
