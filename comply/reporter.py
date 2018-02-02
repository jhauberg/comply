# coding=utf-8

import os

from collections import OrderedDict

from comply.printing import printdiag, printout
from comply.util import truncated, Ellipsize


class Reporter:
    def __init__(self, is_verbose: bool=False):
        self.is_verbose = is_verbose

    def report_before_checking(self, path: str):
        if self.is_verbose:
            diag = 'Checking \'{0}\'... '.format(truncated(path))

            printdiag(diag, end='')

    def report_before_reporting(self, violations: list):
        if self.is_verbose:
            diag = 'Found {0} violations'.format(len(violations))

            printdiag(diag)

    def report(self, violations: list, path: str):
        printout('{0}: {1}'.format(path, violations))


class StandardReporter(Reporter):
    """ Provides violation output (including suggestions) formatted for human readers. """

    def __init__(self, reports_solutions: bool=False):
        Reporter.__init__(self)

        self.reports_solutions = reports_solutions

    def report(self, violations: list, path: str):
        occurences = []
        solutions = OrderedDict() if self.reports_solutions else None

        for violation in violations:
            location = '{0}:{1}'.format(
                truncated(path, length=40, options=Ellipsize.options(at=Ellipsize.middle)),
                violation.where)

            reason = '[{0}] {1}'.format(violation.which.name, violation.which.reason(violation))

            if len(violation.what) > 0:
                occurence = '{0} {1}'.format(location, violation.what)
            else:
                occurence = location

            occurences.append((occurence, reason))

            if self.reports_solutions:
                solutions[occurence] = violation.which.solution(violation)

        if self.reports_solutions:
            solutions = without_duplicates(solutions)

        for occurence, reason in occurences:
            output = '{0} -> {1}'.format(occurence, reason)

            printout(output)

            if self.reports_solutions and occurence in solutions:
                printout('> {0}'.format(solutions[occurence]))


class ClangReporter(Reporter):
    """ Provides violation output formatted in a Clang-like fashion. """

    def report(self, violations: list, path: str):
        for violation in violations:
            absolute_path = os.path.abspath(path)

            line, column = violation.where

            if column > 0:
                location = '{0}:{1}:{2}:'.format(absolute_path, line, column)
            else:
                location = '{0}:{1}:'.format(absolute_path, line)

            reason = '{0} [{1}]'.format(violation.which.reason(violation), violation.which.name)
            output = '{0} warning: {1}'.format(location, reason)

            printout(output)


def without_duplicates(pairs: OrderedDict) -> dict:
    unique_pairs = {}

    for key, value in reversed(pairs.items()):
        if value not in unique_pairs.values():
            unique_pairs[key] = value

    return unique_pairs
