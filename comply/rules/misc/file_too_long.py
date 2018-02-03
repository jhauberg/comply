# coding=utf-8

from comply.rule import Rule, RuleViolation

from comply.printing import Colors


class FileTooLong(Rule):
    def __init__(self):
        Rule.__init__(self, name='file-too-long',
                      description='File has too many lines ({0} > {1}).',
                      suggestion='Consider refactoring and splitting to separate units.')

    MAX = 600

    def reason(self, offender: 'RuleViolation'=None):
        rep = super().reason(offender)

        length = offender.meta['length'] if 'length' in offender.meta.keys() else 0

        return rep.format(length, FileTooLong.MAX)

    def violate(self, at: (int, int), offending_lines: list=list(), meta: dict=None) -> RuleViolation:
        breaker_linenumber, breaker_line = offending_lines[1]

        offending_lines.insert(1, (breaker_linenumber, '---'))

        for i, (linenumber, line) in enumerate(offending_lines):
            if i > 0:
                # mark breaker and everything below it
                offending_lines[i] = (linenumber, Colors.bad + line + Colors.clear)

        return super().violate(at, offending_lines, meta)

    def collect(self, text: str, filename: str, extension: str) -> list:
        offenders = []

        length = text.count('\n')

        if length > FileTooLong.MAX:
            lines = text.splitlines()  # without newlines

            offending_line_index = FileTooLong.MAX
            offending_lines = [(offending_line_index, lines[offending_line_index - 1]),
                               (offending_line_index + 1, lines[offending_line_index]),
                               (offending_line_index + 2, lines[offending_line_index + 1])]

            offender = self.violate(at=(offending_line_index + 1, 0),
                                    offending_lines=offending_lines,
                                    meta={'length': length})

            offenders.append(offender)

        return offenders

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
