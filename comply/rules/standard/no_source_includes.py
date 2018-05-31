# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN


class NoSourceIncludes(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-src-includes',
                      description='Don\'t include source files',
                      suggestion='Find a way to remove the #include directive.')

    pattern = re.compile(INCLUDE_PATTERN)

    def collect(self, file: CheckFile):
        offenders = []

        for inclusion in self.pattern.finditer(file.stripped):
            # note that we can't just grab the string captured by the 'filename' group in this case
            # because we're searching on stripped source (which might have stripped literals)
            included_file = file.original[inclusion.start('filename'):inclusion.end('filename')]
            included_file = included_file.strip()

            if included_file.endswith('.c'):
                offender = self.violate_at_match(file, at=inclusion)
                offenders.append(offender)

        return offenders
