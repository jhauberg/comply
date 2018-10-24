# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_PROT_PATTERN, FUNC_IMPL_PATTERN

from comply.printing import Colors


class NoAmbiguousFunctions(Rule):
    """ Don't provide ambiguous function declarations.

    This mainly pertains to functions with parameter-less declarations.
    <br/><br/>
    In C, a function declaration with no parameters is ambiguous, as it implicitly declares a
    function that can take an arbitrary number of parameters.

    References:

      * [Empty parameter list in C function, do you write func(void) or func()?](https://blog.zhaw.ch/icclab/empty-parameter-list-in-c-function-do-you-write-funcvoid-or-func/)
    """

    def __init__(self):
        Rule.__init__(self, name='no-ambiguous-funcs',
                      description='Ambiguous function declaration',
                      suggestion='Add \'void\' to indicate that this is a zero-parameter function.')

    pattern = re.compile(FUNC_PROT_PATTERN)

    def augment_by_color(self, violation: RuleViolation):
        # assume only one offending line
        line_index = violation.index_of_starting_line()

        function_line_number, function_line = violation.lines[line_index]

        insertion_index = violation.meta['insertion_index']

        violation.lines[line_index] = (function_line_number,
                                       function_line[:insertion_index] +
                                       Colors.GOOD + 'void' + Colors.RESET +
                                       function_line[insertion_index:])

    def collect(self, file: CheckFile):
        offenders = []

        text = file.collapsed

        for function_match in self.pattern.finditer(text):
            function_parameters = function_match.group('params')

            if len(function_parameters.strip()) > 0:
                # this function has explicitly specified parameters; move on
                continue

            offending_index = function_match.start('name')

            offending_line_number, offending_column = file.line_number_at(offending_index)

            character_range = (function_match.start(),
                               function_match.end())

            offending_lines = file.lines_in_character_range(character_range)

            function_parameters_starting_index = function_match.start('params')

            _, insertion_column = file.line_number_at(function_parameters_starting_index)

            offender = self.violate(at=(offending_line_number, offending_column),
                                    lines=offending_lines,
                                    meta={'insertion_index': insertion_column - 1})

            offenders.append(offender)

        return offenders

    @property
    def triggers(self):
        return [
            'void ↓func();'
        ]

    @property
    def nontriggers(self):
        return [
            'void func(void);'
        ]


class ExplicitlyVoidFunctions(NoAmbiguousFunctions):
    """ Always specify parameters as `void` if a function implementation takes zero parameters.

    Technically, this is not required for the compiler to do its job, but being explicit helps in
    keeping a clear and consistent interface.
    """

    def __init__(self):
        NoAmbiguousFunctions.__init__(self)

        self.name = 'explicitly-void-funcs'
        self.description = 'Parameter-less function does not specify parameters as \'void\''
        self.pattern = re.compile(FUNC_IMPL_PATTERN)

    @property
    def triggers(self):
        return [
            'void ↓func() { ... }'
        ]

    @property
    def nontriggers(self):
        return [
            'void func(void) { ... }'
        ]
