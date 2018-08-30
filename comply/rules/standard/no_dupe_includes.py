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

        included_filenames = []

        for inclusion in self.pattern.finditer(file.stripped):
            included_filename = file.original[inclusion.start('filename'):
                                              inclusion.end('filename')]

            if included_filename not in included_filenames:
                included_filenames.append(included_filename)
            else:
                offender = self.violate_at_match(file, at=inclusion)
                offenders.append(offender)

        return offenders

    @property
    def triggers(self):
        return [
            ('#include <header.h>\n'
             '↓#include <header.h>'),
            ('#include "header.h"\n'
             '↓#include "header.h"'),
            ('#include <header.h>\n'
             '↓#include "header.h"'),
            ('#include "header.h"\n'
             '↓#include <header.h>')
        ]

    @property
    def nontriggers(self):
        return [
            ('#include <header.h>\n'
             '#include <other_header.h>\n'
             '#include "and_another_header.h"\n')
        ]
