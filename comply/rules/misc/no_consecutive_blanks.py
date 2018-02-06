# coding=utf-8

from comply.rules import Rule, RuleViolation

from comply.printing import Colors


class NoConsecutiveBlanks(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-consecutive-blanks',
                      description='Too many consecutive blank lines ({0} > {1})',
                      suggestion='Remove excess blank lines.')

    MAX = 1

    def reason(self, violation: RuleViolation=None):
        count = violation.meta['count'] if 'count' in violation.meta else 0

        return super().reason(violation).format(
            count, NoConsecutiveBlanks.MAX)

    def augment(self, violation: RuleViolation):
        for i, (linenumber, line) in enumerate(violation.lines):
            if i != len(violation.lines) - 1:
                # only mark the excess blanks
                color = Colors.bad if i > 0 else Colors.clear

                violation.lines[i] = (linenumber, color + '~~~~~~~~' + Colors.clear)

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        lines = text.splitlines()  # without newlines

        consecutive_blanks = 0

        def trigger(at, lines, count):
            offender = self.violate(at, lines, meta={'count': count})
            offenders.append(offender)

        def previous_lines(lines, from_index, count):
            prev = []

            for line_index in range(from_index - count, from_index + 1):
                line = lines[line_index] if line_index < len(lines) else 'EOF'

                prev.append((line_index + 1, line))

            return prev

        line_index = 0

        for line in lines:
            if not line.strip():
                consecutive_blanks += 1
            else:
                if consecutive_blanks > NoConsecutiveBlanks.MAX:
                    trigger(at=(line_index + 1, 0),
                            lines=previous_lines(lines, line_index, consecutive_blanks),
                            count=consecutive_blanks)

                consecutive_blanks = 0

            line_index += 1

        if consecutive_blanks > NoConsecutiveBlanks.MAX:
            trigger(at=(line_index, 0),  # EOF
                    lines=previous_lines(lines, line_index, consecutive_blanks),
                    count=consecutive_blanks)

        return offenders
