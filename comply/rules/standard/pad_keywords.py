# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import KEYWORDS

from comply.printing import Colors


class PadKeywords(Rule):
    def __init__(self):
        Rule.__init__(self, name='pad-keywords',
                      description='Keywords should be padded with space on both sides',
                      suggestion='Add a single whitespace to the {left_or_right} of \'{keyword}\'.')

    neighbor_pattern = r'[;{}()]'

    pattern = re.compile(r'\b({keywords}){neighbors}|{neighbors}({keywords})\b'.format(
        keywords=KEYWORDS,
        neighbors=neighbor_pattern))

    def augment(self, violation: RuleViolation):
        line_number, line = violation.lines[0]

        from_index, to_index = violation.meta['range']

        augmented_line = (line[:from_index] +
                          Colors.bad + line[from_index:to_index] + Colors.clear +
                          line[to_index:])

        violation.lines[0] = (line_number, augmented_line)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.stripped

        for keyword_match in self.pattern.finditer(text):
            keyword_group_index = keyword_match.lastindex

            # note that we grab the starting index of the actual keyword
            offending_index = keyword_match.start(keyword_group_index)
            offending_line_number, offending_column = file.line_number_at(offending_index)

            length = keyword_match.end() - keyword_match.start()

            # note that to mark the range, we go from the starting index of the full match
            _, offending_range_column = file.line_number_at(keyword_match.start())

            offending_range = (offending_range_column - 1,
                               offending_range_column - 1 + length)

            right_group_index = 1  # the first capture group; only one group will be matched

            left_or_right = 'right' if keyword_group_index == right_group_index else 'left'

            keyword = keyword_match.group(keyword_group_index)

            line = file.lines[offending_line_number - 1]

            offender = self.violate(at=(offending_line_number, offending_column),
                                    lines=[(offending_line_number, line)],
                                    meta={'left_or_right': left_or_right,
                                          'keyword': keyword,
                                          'range': offending_range})

            offenders.append(offender)

        return offenders
