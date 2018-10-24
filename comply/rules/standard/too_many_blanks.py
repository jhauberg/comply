# coding=utf-8

from comply.rules.rule import *

from comply.printing import Colors


class TooManyBlanks(Rule):
    """ Don't add more than 1 blank line, neither leading, nor following, any line of code.

    Blank lines are occasionally used as a way of partitioning or grouping chunks of logically
    separated code, but this is not recommended.
    """

    def __init__(self):
        Rule.__init__(self, name='too-many-blanks',
                      description='Too many consecutive blank lines ({count} > {max})',
                      suggestion='Remove excess blank lines.')

    MAX = 1

    def augment_by_color(self, violation: RuleViolation):
        for i, (linenumber, line) in enumerate(violation.lines):
            if i != len(violation.lines) - 1:
                # only mark the excess blanks
                color = Colors.BAD if i > 0 else Colors.RESET

                violation.lines[i] = (linenumber, color + '~~~~~~~~' + Colors.RESET)

    def collect(self, file: CheckFile):
        offenders = []

        max_lines = TooManyBlanks.MAX

        lines = file.lines  # without newlines

        consecutive_blanks = 0

        def trigger(at, lines, count):
            offender = self.violate(at, lines=lines, meta={'count': count, 'max': max_lines})
            offenders.append(offender)

        def previous_lines(lines, from_index, count):
            prev = []

            for line_index in range(from_index - count, from_index + 1):
                line = lines[line_index] if line_index < len(lines) else 'EOF'

                prev.append((line_index + 1, line))

            return prev

        line_index = 0

        for line in lines:
            if not line.strip():  # line is blank/empty
                consecutive_blanks += 1
            else:
                if consecutive_blanks > max_lines:
                    location = file.line_number_at_start_of(line_index, span_entire_line=True)

                    trigger(at=location,
                            lines=previous_lines(lines, line_index, consecutive_blanks),
                            count=consecutive_blanks)

                consecutive_blanks = 0

            line_index += 1

        if consecutive_blanks > max_lines:
            location = file.line_number_at_start_of(line_index - 1, span_entire_line=True)

            trigger(at=location,  # EOF
                    lines=previous_lines(lines, line_index, consecutive_blanks),
                    count=consecutive_blanks)

        return offenders

    @property
    def triggers(self):
        return [
            ('source with some blank lines\n'
             '\n'
             '\n'
             '▶more source'),
            ('source with some blank lines\n'
             '\n'
             '\n'
             '▶more source\n'
             'asdasd')
        ]

    @property
    def nontriggers(self):
        return [
            ('source with a single blank line\n'
             '\n'
             'more source')
        ]
