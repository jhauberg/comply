# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import FUNC_BOTH_PATTERN

from comply.printing import Colors


class NoRedundantSize(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-redundant-size',
                      description='Don\'t specify array sizes in function signatures',
                      suggestion='Remove redundant size specifier \'{size}\'.')

    pattern = re.compile(FUNC_BOTH_PATTERN)

    size_pattern = re.compile(r'\[([^\[\]]+?)\]')

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

        text = file.collapsed

        for function_match in self.pattern.finditer(text):
            function_parameters = function_match.group('params')

            for size_match in self.size_pattern.finditer(function_parameters):
                size = size_match.group(1).strip()

                if len(size) == 0:
                    continue

                if 'static' in size:
                    # some compilers support marking size as static, making it emit diagnostics
                    # when passed an incompatible type
                    continue

                if size == 'const':
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
                offending_line_number, offending_column = file.line_number_at(offending_index)

                character_range = (function_match.start(),
                                   function_match.end())

                offending_lines = file.lines_in(character_range)

                offending_range = (offending_column - 1,
                                   offending_column - 1 + len(size))

                offender = self.violate(at=(offending_line_number, offending_column),
                                        lines=offending_lines,
                                        meta={'size': size,
                                              'range': offending_range})

                offenders.append(offender)

        return offenders
