# coding=utf-8

from comply.rule import Rule, RuleViolation

from comply.printing import Colors


class NoTabs(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-tabs',
                      description='Avoid tabs for alignment (found {0} tabs).',
                      suggestion='Replace each tab with spaces (typically 4).')

    def reason(self, offender: 'RuleViolation'=None):
        rep = super().reason(offender)

        count = offender.meta['count'] if 'count' in offender.meta else 0

        return rep.format(count)

    def violate(self, at: (int, int), offending_lines: list=list(), meta: dict=None) -> RuleViolation:
        # assume only one offending line
        linenumber, line = offending_lines[0]

        line = line.replace('\t', Colors.bad + '~' + Colors.clear)

        lines = [
            (0, Colors.emphasis + 'listing first occurrence:' + Colors.clear),
            (linenumber, line)
        ]

        return super().violate(at, lines, meta)

    def collect(self, text: str, filename: str, extension: str) -> list:
        offenders = []

        tabs_found = text.count('\t')

        if tabs_found > 0:
            first_tab_index = text.find('\t')

            linenumber, column = RuleViolation.where(text, first_tab_index)

            lines = text.splitlines()

            offending_line = (linenumber, lines[linenumber - 1])

            offender = self.violate(at=(linenumber, column),
                                    offending_lines=[offending_line],
                                    meta={'count': tabs_found})

            offenders.append(offender)

        return offenders

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
