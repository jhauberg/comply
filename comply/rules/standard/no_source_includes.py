# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN


class NoSourceIncludes(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-src-includes',
                      description='Don\' include source files',
                      suggestion='Remove #include directive.')

    pattern = re.compile(INCLUDE_PATTERN)

    def collect(self, file: CheckFile):
        offenders = []

        text = file.original  # todo: we actually *do* want comments stripped- just not literals

        for inclusion in self.pattern.finditer(text):
            include_stmt = inclusion.group()

            if include_stmt.endswith('.c'):
                offender = self.violate_at_match(file, at=inclusion)
                offenders.append(offender)

        return offenders
