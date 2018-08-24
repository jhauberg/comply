# coding=utf-8

from comply.rules.rule import *

from comply.printing import Colors


class LineTooLong(Rule):
    """ Don't exceed 80 characters per line.

    Any line of code should fit on the screen it is being viewed on under any scenario;
    whether single file or side-by-side.
    <br/><br/>
    Lines that are too long can be difficult to visually comprehend, and wrapping or
    scrolling makes it harder to read.

    Lines shorter than 80 characters will fit on most viewers, thus improving readability.

    References:

      * Malcolm Inglis: [c-style](https://github.com/mcinglis/c-style#never-have-more-than-79-characters-per-line)
    """

    def __init__(self):
        Rule.__init__(self, name='line-too-long',
                      description='Line is too long ({length} > {max} characters)',
                      suggestion='Use shorter identifiers or split statements to multiple lines.')

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

        max_characters = LineTooLong.MAX

        for i, line in enumerate(file.lines):
            length = len(line)

            if length <= max_characters:
                continue

            line_number = i + 1
            column = max_characters + 1

            offender = self.violate(at=(line_number, column),
                                    lines=[(line_number, line)])

            offender.meta = {'length': length,
                             'max': max_characters}

            offenders.append(offender)

        return offenders
