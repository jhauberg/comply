# coding=utf-8

from comply.rules import Rule, RuleViolation

from comply.printing import Colors


class LineTooLong(Rule):
    def __init__(self):
        Rule.__init__(self, name='line-too-long',
                      description='Line is too long ({0} > {1})',
                      suggestion='Use shorter names or split statements to multiple lines.')

    MAX = 80

    def reason(self, violation: RuleViolation=None):
        length = violation.meta['length'] if 'length' in violation.meta else 0

        return super().reason(violation).format(
            length, LineTooLong.MAX)

    def augment(self, violation: RuleViolation):
        # insert cursor to indicate max line length
        insertion_index = LineTooLong.MAX

        # assume only one offending line
        linenumber, line = violation.lines[0]

        breaker_line = (line[:insertion_index] + Colors.bad + '|' +
                        line[insertion_index:] + Colors.clear)

        violation.lines[0] = (linenumber, breaker_line)

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        index = 0

        for line in text.splitlines(keepends=True):  # keep ends to ensure indexing is correct
            length = len(line)

            characters_except_newline = length - 1

            if characters_except_newline > LineTooLong.MAX:
                offending_index = index + LineTooLong.MAX

                linenumber, column = RuleViolation.where(text, offending_index)

                assert column > LineTooLong.MAX

                # remove any trailing newlines to keep neat prints
                line = without_trailing_newline(line)

                offending_line = (linenumber, line)

                offender = self.violate(at=(linenumber, column),
                                        lines=[offending_line],
                                        meta={'length': characters_except_newline})

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
