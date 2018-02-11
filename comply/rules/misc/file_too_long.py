# coding=utf-8

from comply.rules import Rule, RuleViolation

from comply.printing import Colors


class FileTooLong(Rule):
    def __init__(self):
        Rule.__init__(self, name='file-too-long',
                      description='File has too many lines ({length} > {max})',
                      suggestion='Consider refactoring and splitting to separate units.',
                      expects_original_text=True)

    MAX = 600

    def augment(self, violation: RuleViolation):
        # assume offending line is the second one
        breaker_linenumber, breaker_line = violation.lines[1]
        # add breaker just above offending line
        violation.lines.insert(1, (breaker_linenumber, '---'))

        for i, (linenumber, line) in enumerate(violation.lines):
            if i > 0:
                # mark breaker and everything below it
                violation.lines[i] = (linenumber, Colors.bad + line + Colors.clear)

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        max_length = FileTooLong.MAX
        length = text.count('\n')

        if length > max_length:
            lines = text.splitlines()  # without newlines

            offending_line_index = max_length

            assert len(lines) > offending_line_index + 1

            offending_lines = [(offending_line_index, lines[offending_line_index - 1]),
                               (offending_line_index + 1, lines[offending_line_index]),
                               (offending_line_index + 2, lines[offending_line_index + 1])]

            offender = self.violate(at=(offending_line_index + 1, 0),
                                    lines=offending_lines,
                                    meta={'length': length,
                                          'max': max_length})

            offenders.append(offender)

        return offenders

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
