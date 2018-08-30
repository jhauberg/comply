# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_PROT_PATTERN

from comply.printing import Colors


class NoRedundantName(Rule):
    """ Don't name parameters identically to their type.

    Redundant information is never useful. If a parameter can not be named something meaningful,
    then it is typically better omitted.

    References:

      * Malcolm Inglis: [c-style](https://github.com/mcinglis/c-style#dont-write-argument-names-in-function-prototypes-if-they-just-repeat-the-type)
    """

    def __init__(self):
        Rule.__init__(self, name='no-redundant-name',
                      description='Parameter \'{param}\' is named identically to its type \'{type}\'',
                      suggestion='Rename parameter \'{param}\' to something meaningful or omit it.')

    # note that we intentionally only check function prototypes (implementations often *should*
    # name parameters identically)
    pattern = re.compile(FUNC_PROT_PATTERN)

    params_pattern = re.compile(r'(.*?)(,|$)')
    const_pattern = re.compile(r'(?!const\b)\b\w[^\s]*\b')

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

        for function_match in self.pattern.finditer(file.collapsed):
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

                        offending_line_number, offending_column = file.line_number_at(offending_index)

                        character_range = (function_match.start(),
                                           function_match.end())

                        offending_lines = file.lines_in_character_range(character_range)

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

    @property
    def triggers(self):
        return [

        ]

    @property
    def nontriggers(self):
        return [

        ]
