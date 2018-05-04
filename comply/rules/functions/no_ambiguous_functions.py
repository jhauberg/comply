# coding=utf-8

import re

from comply.rules import Rule, RuleViolation, CheckFile
from comply.rules.functions.pattern import FUNC_PROT_PATTERN, FUNC_IMPL_PATTERN

from comply.printing import Colors


class NoAmbiguousFunctions(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-ambiguous-funcs',
                      description='Avoid ambiguous function declarations',
                      suggestion='Add \'void\' to indicate that this is a zero-parameter function.')

    pattern = re.compile(FUNC_PROT_PATTERN)

    def augment(self, violation: RuleViolation):
        # assume only one offending line
        line_index = violation.index_of_violating_line()

        function_line_number, function_line = violation.lines[line_index]

        insertion_index = violation.meta['insertion_index']

        violation.lines[line_index] = (function_line_number,
                                       function_line[:insertion_index] +
                                       Colors.good + 'void' + Colors.clear +
                                       function_line[insertion_index:])

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        from comply.util.stripping import strip_function_bodies

        text_without_bodies = strip_function_bodies(text)

        for function_match in self.pattern.finditer(text_without_bodies):
            function_parameters = function_match.group('params')
            function_parameters_starting_index = function_match.start('params')

            if len(function_parameters.strip()) == 0:
                offending_index = function_match.start('name')

                offending_line_number, offending_column = RuleViolation.at(offending_index,
                                                                           text)

                character_range = (function_match.start(),
                                   function_match.end())

                offending_lines = RuleViolation.lines_in(character_range,
                                                         file.original)

                _, insertion_column = RuleViolation.at(function_parameters_starting_index,
                                                       text)

                offender = self.violate(at=(offending_line_number, offending_column),
                                        lines=offending_lines,
                                        meta={'insertion_index': insertion_column - 1})

                offenders.append(offender)

        return offenders


class ExplicitlyVoidFunctions(NoAmbiguousFunctions):
    def __init__(self):
        NoAmbiguousFunctions.__init__(self)

        self.name = 'explicitly-void-funcs'
        self.description = 'Parameter-less functions should specify parameters as \'void\''
        self.pattern = re.compile(FUNC_IMPL_PATTERN)
