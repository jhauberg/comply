# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN


class NoDuplicateIncludes(Rule):
    """ Don't include another file more than once per file. """

    def __init__(self):
        Rule.__init__(self, name='no-dupe-includes',
                      description='File already included previously',
                      suggestion='Remove duplicate #include directive.')

    pattern = re.compile(INCLUDE_PATTERN)

    def collect(self, file: CheckFile):
        offenders = []

        include_statements = []

        for inclusion in self.pattern.finditer(file.stripped):
            include_statement = file.original[inclusion.start():inclusion.end()]

            if include_statement not in include_statements:
                include_statements.append(include_statement)
            else:
                offender = self.violate_at_match(file, at=inclusion)
                offenders.append(offender)

        return offenders
