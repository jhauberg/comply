# coding=utf-8

import re

from comply.rules import Rule, RuleViolation

from comply.printing import Colors


class NoAttachedStars(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-attached-stars',
                      description='Pointer stars should be padded with space on both sides',
                      suggestion='Add spacing to the {left_or_right} of the pointer star.')

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        augmented_line = (line[:from_index] +
                          Colors.bad + line[from_index:to_index] + Colors.clear +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        pattern = r'\((?P<params>[^!@#$+%^{};()]*)\)'

        lines = text.splitlines()


        for function_match in re.finditer(pattern, text):
            function_parameters = function_match.group('params')

            star_pattern = r'\*[^\s,*]|[^\s*]\*'

            for star_match in re.finditer(star_pattern, function_parameters):
                is_probably_dereference = True

                for i in range(star_match.start() - 1, 0, -1):
                    if function_parameters[i] == ',':
                        break

                    if function_parameters[i] != ' ':
                        is_probably_dereference = False

                        break

                if not is_probably_dereference:
                    offending_index = function_match.start('params') + star_match.start()

                    offending_line_number, offending_column = RuleViolation.at(offending_index,
                                                                               text)

                    line = lines[offending_line_number - 1]

                    length = star_match.end() - star_match.start()

                    offending_range = (offending_column - 1, offending_column - 1 + length)

                    left_or_right = 'right' if star_match.group().startswith('*') else 'left'

                    offender = self.violate(at=(offending_line_number, offending_column),
                                            lines=[(offending_line_number, line)],
                                            meta={'left_or_right': left_or_right,
                                                  'range': offending_range})

                    offenders.append(offender)

        return offenders
