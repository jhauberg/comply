# coding=utf-8

from comply.rule import Rule, RuleViolation
from comply.util import truncated, Ellipsize


class LineTooLong(Rule):
    def __init__(self):
        Rule.__init__(self, name='line-too-long',
                      description='Line is too long ({0} > {1}).',
                      suggestion='Use shorter names or split statements to multiple lines.')

    MAX = 80

    def reason(self, offender: 'RuleViolation'=None):
        rep = super().reason(offender)

        length = offender.meta['length'] if 'length' in offender.meta.keys() else 0

        return rep.format(length, LineTooLong.MAX)

    def violate(self, at: (int, int), offending_lines: list=list(), meta: dict=None) -> RuleViolation:
        # insert cursor to indicate max line length
        insertion_index = LineTooLong.MAX

        # assume only one offending line
        linenumber, line = offending_lines[0]

        line = (line[:insertion_index] + '|' +
                line[insertion_index:])

        # remove any trailing newlines to keep neat prints
        line = without_trailing_newline(line)

        return super().violate(at, [(linenumber, line)], meta)

    def collect(self, text: str, filename: str, extension: str) -> list:
        offenders = []

        index = 0

        for line in text.splitlines(keepends=True):  # keep ends to ensure indexing is correct
            length = len(line)

            characters_except_newline = length - 1

            if characters_except_newline > LineTooLong.MAX:
                offending_index = index + LineTooLong.MAX

                linenumber, column = RuleViolation.where(text, offending_index)

                offending_line = (linenumber, line)

                offender = self.violate(at=(line, column),
                                        offending_lines=[offending_line],
                                        meta={'length': characters_except_newline})

                offenders.append(offender)

            index += length

        return offenders


def without_trailing_newline(text: str) -> str:
    if text.endswith('\r\n'):
        return text[:-2]

    if text.endswith('\n'):
        return text[:-1]

    return text
