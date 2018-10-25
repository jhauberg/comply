# coding=utf-8

import re

from comply.rules.rule import *

from comply.printing import Colors


class PadPointers(Rule):
    """ Always pad pointer declarations with space on both sides.

    Having no padding for `*`'s makes for an inconsistent reading of types- especially when
    combined with `const` qualifiers.
    <br/><br/>
    See <tt>const-on-right</tt>.
    <br/><br/>
    Additionally, padding provides a clear separation between a declaration and a pointer dereference.

    References:

      * Malcolm Inglis: [c-style](https://github.com/mcinglis/c-style#always-put-const-on-the-right-and-read-types-right-to-left)
    """

    def __init__(self):
        Rule.__init__(self, name='pad-pointers',
                      description='Pointer declaration not padded with whitespace',
                      suggestion='Add a single whitespace to the {left_or_right} of the asterisk.')

    pattern = re.compile(r'\*\w|\w\*')

    def augment_by_color(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range']

        augmented_line = (line[:from_index] +
                          Colors.BAD + line[from_index:to_index] + Colors.RESET +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        for star_match in self.pattern.finditer(text):
            offending_index = star_match.start()

            is_probably_dereference = True

            index_left_of_star = offending_index + star_match.group().index('*') - 1

            for i in range(index_left_of_star, 0, -1):
                c = text[i]

                if c in [',', ';', ':', '?', '=', '!', '|', '&', '+', '-', '/', '(', ')', '[', ']',
                         '\r', '\n']:
                    # found a character that signifies this is probably a dereferencing pointer
                    break
                else:
                    if c not in [' ', '\t']:
                        # found a character that signifies this is likely a declaration pointer
                        is_probably_dereference = False

                        break

            if not is_probably_dereference:
                offending_line_number, offending_column = file.line_number_at(offending_index)

                line = file.lines[offending_line_number - 1]

                length = star_match.end() - star_match.start()

                offending_range = (offending_column - 1, offending_column - 1 + length)
                offending_snippet = star_match.group()

                should_pad_right = offending_snippet.startswith('*')

                left_or_right = 'right' if should_pad_right else 'left'

                offender = self.violate(at=(offending_line_number, offending_column + (1 if not should_pad_right else 0)),
                                        lines=[(offending_line_number, line)],
                                        meta={'left_or_right': left_or_right,
                                              'range': offending_range})

                offenders.append(offender)

        return offenders

    @property
    def triggers(self):
        return [
            'char const ↓*a = "abc";',
            '(struct command↓*)cmd',
            'return *((uint64_t↓*)&index);'
        ]

    @property
    def nontriggers(self):
        return [
            'char const * a = "abc";',
            'char const a = *ptr;',
            '*ptr = a;',
            'char const a = b ? c : *ptr;',
            'char const a = b ? *ptr : c;'
        ]
