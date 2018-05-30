# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN


class NoDuplicateIncludes(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-dupe-includes',
                      description='File already included previously',
                      suggestion='Remove duplicate #include directive.')

    pattern = re.compile(INCLUDE_PATTERN)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.original  # todo: we actually *do* want comments stripped- just not literals

        include_stmts = []

        for inclusion in self.pattern.finditer(text):
            include_stmt = inclusion.group()

            if include_stmt not in include_stmts:
                include_stmts.append(include_stmt)
            else:
                offender = self.violate_at_match(file, at=inclusion)
                offenders.append(offender)

        return offenders
