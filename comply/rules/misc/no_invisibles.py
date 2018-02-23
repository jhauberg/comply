# coding=utf-8

from comply.rules import Rule, RuleViolation

from comply.printing import Colors


class NoInvisibles(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-invisibles',
                      description='Avoid invisible characters (found {count})',
                      suggestion='Delete each occurence or replace with a space.',
                      expects_original_text=True)

    INVISIBLES = ['\u200b', '\u200c', '\u200d',
                  '\uFEFF']

    @property
    def severity(self):
        return RuleViolation.DENY

    def augment(self, violation: RuleViolation):
        # assume only one offending line
        linenumber, line = violation.lines[0]

        for invisible in NoInvisibles.INVISIBLES:
            line = line.replace(invisible, Colors.bad + '~' + Colors.clear)

        augmented_line = (linenumber, line)

        count = violation.meta['count'] if 'count' in violation.meta else 0
        count_in_line = violation.meta['count_in_line'] if 'count_in_line' in violation.meta else 0

        if count > count_in_line:
            violation.lines = [
                (0, Colors.emphasis + 'listing first occurrence:' + Colors.clear),
                augmented_line
            ]
        else:
            violation.lines[0] = augmented_line

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        invisibles_found = 0

        for invisible in NoInvisibles.INVISIBLES:
            invisibles_found += text.count(invisible)

        if invisibles_found > 0:
            first_invis_index = -1

            for invisible in NoInvisibles.INVISIBLES:
                first_invis_index = text.find(invisible)

                if first_invis_index != -1:
                    break

            assert first_invis_index != -1

            linenumber, column = RuleViolation.at(first_invis_index, text)

            lines = text.splitlines()

            offending_line = (linenumber, lines[linenumber - 1])

            invisibles_in_line = 0

            for invisible in NoInvisibles.INVISIBLES:
                invisibles_in_line += offending_line[1].count(invisible)

            offender = self.violate(at=(linenumber, column),
                                    lines=[offending_line],
                                    meta={'count': invisibles_found,
                                          'count_in_line': invisibles_in_line})

            offenders.append(offender)

        return offenders

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
