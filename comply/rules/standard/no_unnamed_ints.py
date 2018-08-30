# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_PROT_PATTERN

from comply.printing import Colors


class NoUnnamedInts(Rule):
    """ Provide meaningful names for integer parameters if able.

    The majority of function prototypes will suffer from having unnamed integer parameters,
    as their meaning can otherwise be difficult to derive.
    <br/><br/>
    There are exceptions, of course; a good example is a math function such as `max(int, int)`
    where adding parameter names (e.g. `int a` and `int b`) would not add value or make it
    easier to understand.
    <br/><br/>
    In general, however, it is almost always preferable to provide parameter names.
    """

    def __init__(self):
        Rule.__init__(self, name='no-unnamed-ints',
                      description='Integer parameter is unnamed',
                      suggestion='Provide a name for this parameter.')

    pattern = re.compile(FUNC_PROT_PATTERN)

    # todo: long long would not be matched
    int_types = 'uint8_t|uint16_t|uint32_t|uint64_t|int8_t|int16_t|int32_t|int64_t|int|short|long'

    unnamed_int_pattern = re.compile(r'\b({types})(?:\s*?(?:,|$))'.format(
        types=int_types))

    def augment(self, violation: RuleViolation):
        # assume only one offending line
        line_index = violation.index_of_starting_line()

        function_line_number, function_line = violation.lines[line_index]

        insertion_index = violation.meta['insertion_index']

        violation.lines[line_index] = (function_line_number,
                                       function_line[:insertion_index] +
                                       Colors.GOOD + ' name' + Colors.RESET +
                                       function_line[insertion_index:])

    def collect(self, file: CheckFile):
        offenders = []

        text = file.collapsed

        for function_match in self.pattern.finditer(text):
            function_parameters = function_match.group('params')
            function_parameters_starting_index = function_match.start('params')

            for unnamed_match in self.unnamed_int_pattern.finditer(function_parameters):
                offending_index = (function_parameters_starting_index +
                                   unnamed_match.start(1))

                offending_line_number, offending_column = file.line_number_at(offending_index)

                character_range = (function_match.start(),
                                   function_match.end())

                offending_lines = file.lines_in_character_range(character_range)

                _, insertion_column = file.line_number_at(
                    function_parameters_starting_index + unnamed_match.end(1))

                offender = self.violate(at=(offending_line_number, offending_column),
                                        lines=offending_lines,
                                        meta={'insertion_index': insertion_column - 1})

                offenders.append(offender)

        return offenders

    @property
    def severity(self):
        return RuleViolation.ALLOW

    @property
    def triggers(self):
        return [
            'void func(↓int);',
            'void func(  ↓int);',
            'void func(↓int  );',
            'void func(  ↓int  );',
            ('void func(↓int,\n'
             '          unsigned ↓int);')
        ]

    @property
    def nontriggers(self):
        return [
            'void func(int a);',
            'void func(int    a);',
            ('void func(int\n'
             '          a);'),
            'void func(struct point);'
        ]
