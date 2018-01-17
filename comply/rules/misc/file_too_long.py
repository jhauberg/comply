# coding=utf-8

from comply.rule import Rule, RuleOffender
from comply.util import truncated


class FileTooLong(Rule):
    def __init__(self):
        Rule.__init__(self, name='file-too-long',
                      description='File has too many lines ({0} > {1}).',
                      suggestion='Consider refactoring and splitting to separate units.')

    max_lines = 600

    def representation(self, offender: 'RuleOffender'=None):
        rep = super().representation(offender)

        length = offender.meta['length'] if 'length' in offender.meta.keys() else 0

        return rep.format(length, self.max_lines)

    def offend(self, at: (int, int), offending_text: str, meta: dict = None) -> RuleOffender:
        what = '\'{0}\''.format(truncated(offending_text))

        return super().offend(at, what, meta)

    def collect(self, text: str) -> list:
        offenders = []

        length = text.count('\n')

        if length > self.max_lines:
            lines = text.splitlines()  # without newlines

            offending_line_index = self.max_lines
            offending_line = lines[offending_line_index]

            offender = self.offend(at=(offending_line_index, 1),
                                   offending_text=offending_line,
                                   meta={'length': length})

            offenders.append(offender)

        return offenders
