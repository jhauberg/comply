# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN


class NoSourceIncludes(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-src-includes',
                      description='Don\'t include source files',
                      suggestion='Remove #include directive.')

    pattern = re.compile(INCLUDE_PATTERN)

    def collect(self, file: CheckFile):
        offenders = []

        for inclusion in self.pattern.finditer(file.original):
            included_file = inclusion.group('filename').strip()

            if included_file.endswith('.c'):
                offender = self.violate_at_match(file, at=inclusion)
                offenders.append(offender)

        return offenders
