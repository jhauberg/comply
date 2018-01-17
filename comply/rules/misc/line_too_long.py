# coding=utf-8

from comply.rule import Rule, RuleOffender
from comply.util import truncated, Ellipsize


class LineTooLong(Rule):
    def __init__(self):
        Rule.__init__(self, name='line-too-long',
                      description='Line is too long ({0} > {1}).',
                      suggestion='Use shorter names or split statements to multiple lines.')

    max_line_length = 80

    def representation(self, offender: 'RuleOffender'=None):
        rep = super().representation(offender)

        length = offender.meta['length'] if 'length' in offender.meta.keys() else 0

        return rep.format(length, self.max_line_length)

    def offend(self, at: (int, int), offending_text: str, meta: dict = None) -> RuleOffender:
        # insert cursor to indicate max line length
        text = (offending_text[:self.max_line_length] + '|' +
                offending_text[self.max_line_length:])
        # remove any trailing newlines to keep neat prints
        offending_text = without_trailing_newline(text)

        what = '\'{0}\''.format(
            truncated(offending_text, length=self.max_line_length, ellipsize=Ellipsize.start))

        return super().offend(at, what, meta)

    def collect(self, text: str) -> list:
        offenders = []

        index = 0

        for line in text.splitlines(keepends=True):  # keep ends to ensure indexing is correct
            length = len(line)

            characters_except_newline = length - 1

            if characters_except_newline > self.max_line_length:
                offending_index = index + self.max_line_length - 1

                offender = self.offend(at=RuleOffender.where(text, offending_index),
                                       offending_text=line,
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
