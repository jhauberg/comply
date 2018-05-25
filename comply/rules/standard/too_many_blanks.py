# coding=utf-8

from comply.rules.rule import *

from comply.printing import Colors


class TooManyBlanks(Rule):
    def __init__(self):
        Rule.__init__(self, name='too-many-blanks',
                      description='Too many consecutive blank lines ({count} > {max})',
                      suggestion='Remove excess blank lines.')

    MAX = 1

    def augment(self, violation: RuleViolation):
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
            offender = self.violate(at, lines, meta={'count': count,
                                                     'max': max_lines})
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
                    trigger(at=(line_index + 1, 0),
                            lines=previous_lines(lines, line_index, consecutive_blanks),
                            count=consecutive_blanks)

                consecutive_blanks = 0

            line_index += 1

        if consecutive_blanks > max_lines:
            trigger(at=(line_index, 0),  # EOF
                    lines=previous_lines(lines, line_index, consecutive_blanks),
                    count=consecutive_blanks)

        return offenders
