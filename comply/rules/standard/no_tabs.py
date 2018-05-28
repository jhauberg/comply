# coding=utf-8

from comply.rules.rule import *

from comply.printing import Colors, supports_unicode


class NoTabs(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-tabs',
                      description='Don\'t use tabs to keep line lengths consistent ({count} tabs)',
                      suggestion='Replace each tab with spaces (typically 4).')

    TAB = '\t'

    def augment(self, violation: RuleViolation):
        # assume only one offending line
        linenumber, line = violation.lines[0]

        replacement_char = '⇥' if supports_unicode() else '~'

        augmented_line = (linenumber,
                          line.replace(NoTabs.TAB, Colors.BAD + replacement_char + Colors.RESET))

        count = violation.meta['count'] if 'count' in violation.meta else 0
        count_in_line = violation.meta['count_in_line'] if 'count_in_line' in violation.meta else 0

        if count > count_in_line:
            violation.lines = [
                (None, Colors.EMPHASIS + '(listing first occurrence)' + Colors.RESET),
                augmented_line
            ]
        else:
            violation.lines[0] = augmented_line

    def collect(self, file: CheckFile):
        offenders = []

        text = file.original

        tabs_found = text.count(NoTabs.TAB)

        if tabs_found > 0:
            first_tab_index = text.find(NoTabs.TAB)

            linenumber, column = file.line_number_at(first_tab_index)

            offending_line = (linenumber, file.lines[linenumber - 1])

            tabs_in_line = offending_line[1].count(NoTabs.TAB)

            offender = self.violate(at=(linenumber, column),
                                    lines=[offending_line],
                                    meta={'count': tabs_found,
                                          'count_in_line': tabs_in_line})

            offenders.append(offender)

        return offenders

    @property
    def severity(self):
        return RuleViolation.DENY

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
