# coding=utf-8

import re

from comply.rules import Rule, RuleViolation
from comply.rules.functions.pattern import FUNC_BOTH_PATTERN

from comply.printing import Colors


class NoRedundantSize(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-redundant-size',
                      description='Don\'t specify array sizes in function signatures',
                      suggestion='Remove redundant size specifier \'{size}\'.')

    def augment(self, violation: RuleViolation):
        function_linenumber, function_line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        augmented_line = (function_line[:from_index] +
                          Colors.bad + function_line[from_index:to_index] + Colors.clear +
                          function_line[to_index:])

        leading_space = violation.meta['leading_space'] if 'leading_space' in violation.meta else 0

        violation.lines[0] = (function_linenumber, (' ' * leading_space) + augmented_line)

    pattern = re.compile(FUNC_BOTH_PATTERN)

    size_pattern = re.compile(r'\[([^\[\]]+?)\]')

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        from comply.util.stripping import strip_function_bodies

        # weed out potential false-positives by stripping the bodies of function implementations
        text_without_bodies = strip_function_bodies(text)

        for function_match in self.pattern.finditer(text_without_bodies):
            function_result = function_match.group()
            function_parameters = function_match.group('params')

            for size_match in self.size_pattern.finditer(function_parameters):
                size = size_match.group(1).strip()

                if len(size) == 0:
                    continue

                if 'static' in size:
                    # some compilers support marking size as static, making it emit diagnostics
                    # when passed an incompatible type
                    continue

                if 'const' in size:
                    # the const qualifier can be used to indicate that the pointer name is const
                    continue

                # determine whether parameter is like: `int (*arr)[10]` in which case it should
                # not violate the rule as compilers will enforce the size limit
                is_probably_enforced = False
                found_ending_paren = False

                for i in range(size_match.start(), 0, -1):
                    c = function_parameters[i]

                    if c == ',':
                        break

                    if c == '(':
                        if found_ending_paren:
                            is_probably_enforced = True

                        break

                    if c == ')':
                        found_ending_paren = True

                if is_probably_enforced:
                    continue

                offending_index = function_match.start('params') + size_match.start(1)

                function_linenumber, function_column = RuleViolation.at(offending_index,
                                                                        text_without_bodies)

                _, leading_space = RuleViolation.at(function_match.start(),
                                                    text_without_bodies)

                params_start_index = function_match.start('params') - function_match.start()

                size_start = params_start_index + size_match.start(1)
                size_end = params_start_index + size_match.end(1)

                offender = self.violate(at=(function_linenumber, function_column),
                                        lines=[(function_linenumber, function_result)],
                                        meta={'size': size,
                                              'leading_space': leading_space - 1,
                                              'range': (size_start, size_end)})

                offenders.append(offender)

        return offenders
