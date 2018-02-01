# coding=utf-8

import os

from collections import OrderedDict

from comply.util import truncated, Ellipsize


class Reporter:
    """ Provides violation output (including suggestions) formatted for human readers. """

    def __init__(self, reports_solutions: bool=False):
        self.reports_solutions = reports_solutions

    def report_before_checking(self, path: str):
        print('checking \'{0}\'... '.format(truncated(path)), end='')

    def report_before_reporting(self, violations: list):
        print('Found {0} violations'.format(len(violations)))

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

            print(output)

            if self.reports_solutions and occurence in solutions:
                print(solutions[occurence])

        print()


class ClangReporter(Reporter):
    """ Provides violation output formatted in a Clang-like fashion. """

    def __init__(self):
        Reporter.__init__(self, reports_solutions=False)

    def report_before_checking(self, path: str):
        pass

    def report_before_reporting(self, violations: list):
        pass

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

            print(output)


def without_duplicates(pairs: OrderedDict) -> dict:
    unique_pairs = {}

    for key, value in reversed(pairs.items()):
        if value not in unique_pairs.values():
            unique_pairs[key] = value

    return unique_pairs
