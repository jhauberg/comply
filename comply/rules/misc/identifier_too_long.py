# coding=utf-8

import re

from comply.rules import Rule, RuleViolation

from comply.printing import Colors


class IdentifierTooLong(Rule):
    def __init__(self):
        Rule.__init__(self, name='identifier-too-long',
                      description='Identifier is too long ({length} > {max})',
                      suggestion='Use a shorter name.')

    # https://stackoverflow.com/questions/2352209/max-identifier-length
    MAX = 31

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)
        insertion_index = from_index + (violation.meta['max'] if 'max' in violation.meta else 0)

        augmented_line = (line[:insertion_index] +
                          Colors.bad + '|' + line[insertion_index:to_index] + Colors.clear +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        pattern = r'\b\w+\b'

        lines = text.splitlines()

        for identifier_match in re.finditer(pattern, text):
            identifier = identifier_match.group(0)

            line_number, column = RuleViolation.at(identifier_match.start(), text)
            line_index = line_number - 1

            line = lines[line_index]

            max_identifier_length = IdentifierTooLong.MAX

            identifier_length = len(identifier)

            if identifier_length > max_identifier_length:
                identifier_start_index = column - 1
                identifier_end_index = identifier_start_index + identifier_length

                offender = self.violate(at=(line_number, column),
                                        lines=[(line_number, line)],
                                        meta={'length': identifier_length,
                                              'max': max_identifier_length,
                                              'range': (identifier_start_index,
                                                        identifier_end_index)})

                offenders.append(offender)

        return offenders
