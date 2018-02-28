# coding=utf-8

import re

from comply.rules import Rule, RuleViolation

from comply.printing import Colors


class IdentifierTooLong(Rule):
    def __init__(self):
        Rule.__init__(self, name='identifier-too-long',
                      description='Identifier is too long ({length} > {max})',
                      suggestion='Use a shorter name.')

    MAX = 31

    @property
    def severity(self):
        return RuleViolation.ALLOW

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

        lines = text.splitlines()

        def check_identifier(identifier: str, occurrence: (int, int)):
            max_identifier_length = IdentifierTooLong.MAX

            identifier_length = len(identifier)

            if identifier_length > max_identifier_length:
                line_number, column = occurrence
                line_index = line_number - 1

                line = lines[line_index]

                identifier_start_index = column - 1
                identifier_end_index = identifier_start_index + identifier_length

                offender = self.violate(at=occurrence,
                                        lines=[(line_number, line)],
                                        meta={'length': identifier_length,
                                              'max': max_identifier_length,
                                              'range': (identifier_start_index,
                                                        identifier_end_index)})

                offenders.append(offender)

        for identifier_match in re.finditer(r'\b\w+\b', text):
            location = RuleViolation.at(identifier_match.start(), text)

            check_identifier(identifier_match.group(), location)

        return offenders
