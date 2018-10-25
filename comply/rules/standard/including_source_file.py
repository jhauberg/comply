# coding=utf-8

import re

from comply.rules.rule import *
from comply.rules.patterns import INCLUDE_PATTERN


class IncludingSourceFile(Rule):
    """ Don't include source files (.c) in other source files.

    This is advisable to avoid potentially compiling the same unit twice, resulting in multiple
    symbol definitions and linker errors.
    """

    def __init__(self):
        Rule.__init__(self, name='including-source',
                      description='Including source file',
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

    @property
    def triggers(self):
        return [
            '↓#include "source.c"',
            ('// some source file\n'
             '↓#include <source.c>')
        ]

    @property
    def nontriggers(self):
        return [
            ('// some header file\n'
             '#include <file.h>')
        ]
