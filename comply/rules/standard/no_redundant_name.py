# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_PROT_PATTERN

from comply.printing import Colors


class NoRedundantName(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-redundant-name',
                      description='Parameter \'{param}\' should not be named identically to its type \'{type}\'',
                      suggestion='Rename parameter \'{param}\' to something meaningful or omit it.')

    # note that we intentionally only check function prototypes (implementations often *should*
    # name parameters identically)
    pattern = re.compile(FUNC_PROT_PATTERN)

    params_pattern = re.compile(r'(.*?)(,|$)')
    const_pattern = re.compile(r'(?!const\b)\b\w[^\s]*\b')

    def augment(self, violation: RuleViolation):
        line_index = violation.index_of_violating_line()

        function_linenumber, function_line = violation.lines[line_index]

        from_index, to_index = violation.meta['range']

        augmented_line = (function_line[:from_index] +
                          Colors.bad + function_line[from_index:to_index] + Colors.clear +
                          function_line[to_index:])

        violation.lines[line_index] = (function_linenumber, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        from comply.util.stripping import strip_function_bodies

        # weed out potential false-positives by stripping the bodies of function implementations
        text_without_bodies = strip_function_bodies(text)

        for function_match in self.pattern.finditer(text_without_bodies):
            function_parameters = function_match.group('params')

            # naively split by comma; won't yield correct results in all cases,
            # but it doesn't need to for the following logic to work out
            separated_parameters = list(self.params_pattern.finditer(function_parameters))

            for func_param in separated_parameters:
                param = func_param.group(1)
                # matches any word component in a parameter (that isn't 'const')
                type_components = list(self.const_pattern.finditer(param))

                if len(type_components) > 1:  # must be more than two word components in the param
                    func_param_match = type_components[-1]  # last or right-most component
                    func_param_types = type_components[:-1]

                    func_param_name = func_param_match.group()

                    types = [x.group().lower() for x in func_param_types]

                    if func_param_name.lower() in types:
                        param_start = func_param.start(1) + func_param_match.start()

                        offending_index = (function_match.start('params') +
                                           param_start)

                        offending_line_number, offending_column = RuleViolation.at(offending_index,
                                                                                   text)

                        character_range = (function_match.start(),
                                           function_match.end())

                        offending_lines = RuleViolation.lines_in(character_range,
                                                                 file.original)

                        offending_range = (offending_column - 1,
                                           offending_column - 1 + len(func_param_name))

                        param_type = ' '.join(types)

                        offender = self.violate(at=(offending_line_number, offending_column),
                                                lines=offending_lines,
                                                meta={'param': func_param_name,
                                                      'type': param_type,
                                                      'range': offending_range})

                        offenders.append(offender)

        return offenders
