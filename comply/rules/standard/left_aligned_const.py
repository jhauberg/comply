# coding=utf-8

import re

from comply.rules.rule import *

from comply.printing import Colors


class LeftAlignedConst(Rule):
    """ Always place `const` qualifiers to the right of type declarations.

    Placing `const` qualifiers to the left makes for an inconsistent reading of types.

    References:

      * Malcolm Inglis: [c-style](https://github.com/mcinglis/c-style#always-put-const-on-the-right-and-read-types-right-to-left)
    """

    def __init__(self):
        Rule.__init__(self, name='left-aligned-const',
                      description='Left-aligned const qualifier',
                      suggestion='Move \'const\' to the right side of the type declaration.')

    # match both struct/enum and standard type declarations
    type_pattern = r'((?:struct|enum)\s+?.+?\b|.+?\b)'

    pattern = re.compile(r'(?:^|[\n;,(]|(?:static|typedef))\s*\b(const)\b\s+?' + type_pattern)

    def augment_by_color(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range']
        insertion_index = violation.meta['insertion']

        augmented_line = line

        augmented_line = (augmented_line[:insertion_index] +
                          Colors.GOOD + ' const' + Colors.RESET +
                          augmented_line[insertion_index:])

        augmented_line = (augmented_line[:from_index] +
                          Colors.BAD + augmented_line[from_index:to_index] + Colors.RESET +
                          augmented_line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        for match in self.pattern.finditer(file.stripped):
            line_number, column = file.line_number_at(match.start(1))

            offending_index = column - 1
            offending_range = (offending_index, offending_index + len(match.group(1)))

            _, type_column = file.line_number_at(match.start(2))

            insertion_index = type_column - 1 + len(match.group(2))

            start = match.start(1)
            end = match.end(1)

            offender = self.violate_at_character_range(
                file, starting=start, ending=end)

            offender.meta = {
                'range': offending_range,
                'insertion': insertion_index
            }

            offenders.append(offender)

        return offenders

    @property
    def triggers(self):
        return [
            '↓const int a = 1;',
            '↓const int * const b = &a;',
            '↓const struct mytype_t * const c = NULL;',
            '↓const mytype_t * c;',
            'int const a = * (↓const int *)b;',
            ('↓const int32_t\n'
             'my_func(↓const struct mytype_t * const lhs,\n'
             '        ↓const struct mytype_t * const rhs)'),
            # false-positives
            ('int\n'
             '↓const a = 1;')
        ]

    @property
    def nontriggers(self):
        return [
            'int const a = 1;',
            'mytype_t const * c;',
        ]
