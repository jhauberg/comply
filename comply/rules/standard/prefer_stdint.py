# coding=utf-8

import re

from comply.rules.rule import *

from comply.printing import Colors


def match_exactly(int_type: str) -> str:
    return r'\bunsigned\s+{type}\b|\bsigned\s+{type}\b|(\b{type}\b)'.format(
        type=int_type)


def match_signed(int_type: str) -> str:
    return r'\b(signed {type})\b'.format(
        type=int_type)


def match_unsigned(int_type: str) -> str:
    return r'\b(unsigned {type})\b'.format(
        type=int_type)


class PreferStandardInt(Rule):
    def __init__(self):
        Rule.__init__(self, name='prefer-stdint',
                      description='Prefer \'{stdint}\' over \'{int}\'',
                      suggestion='Use \'{stdint}\' instead of \'{int}\'.')

    INT_TYPES = {
        # note that unsigned|signed char is often a perfectly valid choice over uint8_t|int8_t
        # so we don't include that in the table

        'unsigned short':     ('uint16_t', match_unsigned('short')),
        'signed short':       ('int16_t',  match_signed('short')),
        'short':              ('int16_t',  match_exactly('short')),
        'unsigned int':       ('uint32_t', match_unsigned('int')),
        'signed int':         ('int32_t',  match_signed('int')),
        'int':                ('int32_t',  match_exactly('int')),
        'unsigned long':      ('uint64_t', match_unsigned('long')),
        'signed long':        ('int64_t',  match_signed('long')),
        'long':               ('int64_t',  match_exactly('long')),
        'unsigned long long': ('uint64_t', match_unsigned('long long')),
        'signed long long':   ('int64_t',  match_signed('long long')),
        'long long':          ('int64_t',  match_exactly('long long')),
    }

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range'] if 'range' in violation.meta else (0, 0)

        augmented_line = (line[:from_index] +
                          Colors.bad + line[from_index:to_index] + Colors.clear +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        ranges_collected = []

        lines = file.original.splitlines()

        int_types = [int_type for int_type in PreferStandardInt.INT_TYPES]
        # sort by length of type
        sorted_int_types = sorted(int_types, key=lambda int_type: len(int_type.split(' ')))

        # go through each type, but reversed so that we start with the longest types
        for int_type in reversed(sorted_int_types):
            prefer_int_type, pattern = PreferStandardInt.INT_TYPES[int_type]

            for int_match in re.finditer(pattern, text):
                if not int_match.group(1):
                    # expect actual match in first group (a match may occur without a capture)
                    continue

                type_already_collected = False

                for collected_type_start, collected_type_end in ranges_collected:
                    if collected_type_start <= int_match.start(1) <= collected_type_end:
                        type_already_collected = True

                        break

                if type_already_collected:
                    continue

                line_number, column = RuleViolation.at(int_match.start(), text)

                int_type_range = (int_match.start(1), int_match.end(1))

                ranges_collected.append(int_type_range)

                offender = self.violate(at=(line_number, column),
                                        lines=[(line_number, lines[line_number - 1])],
                                        meta={'stdint': prefer_int_type,
                                              'int': int_type,
                                              'range': (column - 1, column - 1 + len(int_type))})

                offenders.append(offender)

        return offenders