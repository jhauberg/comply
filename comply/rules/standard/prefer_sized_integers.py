# coding=utf-8

import re

from comply.rules.rule import *


def match_exactly(int_type: str) -> str:
    return r'\bunsigned\s+{type}\b|\bsigned\s+{type}\b|(\b{type}\b)'.format(
        type=int_type)


def match_signed(int_type: str) -> str:
    return r'\b(signed {type})\b'.format(
        type=int_type)


def match_unsigned(int_type: str) -> str:
    return r'\b(unsigned {type})\b'.format(
        type=int_type)


class PreferSizedIntegers(Rule):
    """ Always use explicitly sized integer types (e.g. `stdint.h`).

    Being explicit about the type and size that you want to use helps improve portability.
    <br/><br/>
    It also increases readability as it makes types read more uniformly, and does away
    entirely with the `unsigned` and `signed` keywords.

    It's worth noting that when sticking with basic types (e.g. `int`), the compiler may just do a
    *better* job than you at deciding which size is actually the optimal choice.
    <br/><br/>
    However, leaving that an implicit choice could result in unexpected issues down the line.
    <br/><br/>
    Being explicit lets you avoid making assumptions. The trade-off is potentially losing some
    (often neglible) performance.

    References:

      * Matt Stancliff: [How to C in 2016: Writing Code- Types](https://matt.sh/howto-c)
    """

    def __init__(self):
        Rule.__init__(self, name='prefer-stdint',
                      description='\'{int}\' used instead of \'{stdint}\'',
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

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        ranges_collected = []

        int_types = [int_type for int_type in PreferSizedIntegers.INT_TYPES]
        # sort by length of type
        sorted_int_types = sorted(int_types, key=lambda int_type: len(int_type.split(' ')))

        # go through each type, but reversed so that we start with the longest types
        for int_type in reversed(sorted_int_types):
            prefer_int_type, pattern = PreferSizedIntegers.INT_TYPES[int_type]

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

                int_type_range = (int_match.start(1), int_match.end(1))

                ranges_collected.append(int_type_range)

                offender = self.violate_at_match(file, at=int_match)
                offender.meta = {'stdint': prefer_int_type,
                                 'int': int_type}

                offenders.append(offender)

        return offenders

    @property
    def triggers(self):
        return [
            'void func(↓int a);'
        ]

    @property
    def nontriggers(self):
        return [
            'void func(int32_t a);'
        ]
