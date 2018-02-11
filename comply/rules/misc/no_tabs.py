# coding=utf-8

from comply.rules import Rule, RuleViolation

from comply.printing import Colors, supports_unicode


class NoTabs(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-tabs',
                      description='Avoid tabs to keep consistent line lengths (found {count} tabs)',
                      suggestion='Replace each tab with spaces (typically 4).')

    TAB = '\t'

    def augment(self, violation: RuleViolation):
        # assume only one offending line
        linenumber, line = violation.lines[0]

        replacement_char = '⇥' if supports_unicode() else '~'

        augmented_line = (linenumber, line.replace(NoTabs.TAB, Colors.bad + replacement_char + Colors.clear))

        count = violation.meta['count'] if 'count' in violation.meta else 0
        count_in_line = violation.meta['count_in_line'] if 'count_in_line' in violation.meta else 0

        if count > count_in_line:
            violation.lines = [
                (None, Colors.emphasis + '(listing first occurrence)' + Colors.clear),
                augmented_line
            ]
        else:
            violation.lines[0] = augmented_line

    def collect(self, text: str, filename: str, extension: str):
        offenders = []

        tabs_found = text.count(NoTabs.TAB)

        if tabs_found > 0:
            first_tab_index = text.find(NoTabs.TAB)

            linenumber, column = RuleViolation.at(first_tab_index, text)

            lines = text.splitlines()

            offending_line = (linenumber, lines[linenumber - 1])

            tabs_in_line = offending_line[1].count(NoTabs.TAB)

            offender = self.violate(at=(linenumber, column),
                                    lines=[offending_line],
                                    meta={'count': tabs_found,
                                          'count_in_line': tabs_in_line})

            offenders.append(offender)

        return offenders

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
