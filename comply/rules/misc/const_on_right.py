# coding=utf-8

import re

from comply.rules import Rule, RuleViolation, CheckFile

from comply.printing import Colors


class ConstOnRight(Rule):
    def __init__(self):
        Rule.__init__(self, name='const-on-right',
                      description='Prefer const qualifiers on the right',
                      suggestion='Place const qualifier to the right of the type declaration.')

    # match both struct/enum and standard type declarations
    type_pattern = r'((?:struct|enum)\s+?.+?\b|.+?\b)'

    pattern = re.compile(r'(?:^|[\n;,(]|(?:static|typedef))\s*\b(const)\b\s+?' + type_pattern)

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)
        insertion_index = violation.meta['insertion'] if 'insertion' in violation.meta else 0

        augmented_line = line

        augmented_line = (augmented_line[:insertion_index] +
                          Colors.good + ' const' + Colors.clear +
                          augmented_line[insertion_index:])

        augmented_line = (augmented_line[:from_index] +
                          Colors.bad + augmented_line[from_index:to_index] + Colors.clear +
                          augmented_line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        lines = file.original.splitlines()

        for match in self.pattern.finditer(text):
            line_number, column = RuleViolation.at(match.start(1), text)

            line = lines[line_number - 1]

            offending_index = column - 1
            offending_range = (offending_index, offending_index + len(match.group(1)))

            type_line_number, type_column = RuleViolation.at(match.start(2), text)

            insertion_index = type_column - 1 + len(match.group(2))

            offender = self.violate(at=(line_number, column),
                                    lines=[(line_number, line)],
                                    meta={'range': offending_range,
                                          'insertion': insertion_index})

            offenders.append(offender)

        return offenders
