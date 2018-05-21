# coding=utf-8

from comply.rules.rule import *

from comply.printing import Colors


class LineTooLong(Rule):
    def __init__(self):
        Rule.__init__(self, name='line-too-long',
                      description='Line is too long ({length} > {max})',
                      suggestion='Use shorter names or split statements to multiple lines.')

    MAX = 80

    def augment(self, violation: RuleViolation):
        # insert cursor to indicate max line length
        insertion_index = violation.meta['max']

        # assume only one offending line
        linenumber, line = violation.lines[0]

        breaker_line = (line[:insertion_index] + Colors.BAD + '|' +
                        line[insertion_index:] + Colors.RESET)

        violation.lines[0] = (linenumber, breaker_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.original

        index = 0

        for line in text.splitlines(keepends=True):  # keep ends to ensure indexing is correct
            length = len(line)

            max_characters = LineTooLong.MAX
            characters_except_newline = length - 1

            if characters_except_newline > max_characters:
                offending_index = index + max_characters

                linenumber, column = file.line_number_at(offending_index)

                assert column > max_characters

                # remove any trailing newlines to keep neat prints
                line = without_trailing_newline(line)

                offending_line = (linenumber, line)

                offender = self.violate(at=(linenumber, column),
                                        lines=[offending_line],
                                        meta={'length': characters_except_newline,
                                              'max': max_characters})

                offenders.append(offender)

            index += length

        return offenders


def without_trailing_newline(text: str) -> str:
    """ Return new text by removing any trailing newline. """

    if text.endswith('\r\n'):
        return text[:-2]

    if text.endswith('\n'):
        return text[:-1]

    return text
