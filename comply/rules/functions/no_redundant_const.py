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

        violation.lines[0] = (function_linenumber, augmented_line)

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        # match prototypes
        pattern = FUNC_PROT_PATTERN
        # match redundant const qualifiers for a list of arguments (e.g. <params>)
        pattern_const = r'\b(const)\b\s*\w*(?:\s*[,)]|$)'

        for function_match in re.finditer(pattern, text):
            function_parameters = function_match.group('params')
            function_result = function_match.group(0)

            function_linenumber, function_column = RuleViolation.where(text, function_match.start())

            for redundant_const_match in re.finditer(pattern_const, function_parameters):
                const_start, const_end = (redundant_const_match.start(1),
                                          redundant_const_match.end(1))

                offending_index = (function_match.start('params') +
                                   const_start)

                linenumber, column = RuleViolation.where(text, offending_index)

                diff = function_match.start('params') - function_match.start()

                offender = self.violate(at=(linenumber, column),
                                        lines=[(function_linenumber, function_result)],
                                        meta={'range': (diff + const_start,
                                                        diff + const_end)})

                offenders.append(offender)

        return offenders
