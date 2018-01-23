# coding=utf-8

import os
import sys

from collections import OrderedDict

from comply.util import truncated, Ellipsize


class Reporter:
    def __init__(self, reports_solutions: bool=False):
        self.reports_solutions = reports_solutions

    def report_before_checking(self, path: str):
        print('checking \'{0}\''.format(path))

    def report_before_reporting(self, violations: list):
        print('{0} violations found:'.format(len(violations)))

    def report(self, violations: list, path: str):
        occurences = []
        solutions = OrderedDict() if self.reports_solutions else None

        for violation in violations:
            location = '{0}:{1}'.format(
                truncated(path, length=28, ellipsize=Ellipsize.middle),
                violation.where)

            reason = '[{0}] {1}'.format(violation.which.name, violation.which.reason(violation))
            occurence = '{0} {1}'.format(location, violation.what)

            occurences.append((occurence, reason))

            if self.reports_solutions:
                solutions[occurence] = violation.which.solution(violation)

        if self.reports_solutions:
            solutions = without_duplicates(solutions)

        for occurence, reason in occurences:
            print('{0} -> {1}'.format(occurence, reason))

            if self.reports_solutions and occurence in solutions:
                print(solutions[occurence])

        print()


class XcodeReporter(Reporter):
    def __init__(self):
        Reporter.__init__(self, reports_solutions=False)

    def report_before_checking(self, path: str):
        pass

    def report_before_reporting(self, violations: list):
        pass

    def report(self, violations: list, path: str):
        for violation in violations:
            absolute_path = os.path.abspath(path)

            location = '{0}:{1}:{2}:'.format(absolute_path, violation.where[0], violation.where[1])
            reason = '{0} [{1}]'.format(violation.which.reason(violation), violation.which.name)

            output = '{0} warning: {1}'.format(location, reason)

            print(output, file=sys.stderr, flush=True)


def without_duplicates(pairs: OrderedDict) -> dict:
    unique_pairs = {}

    for key, value in reversed(pairs.items()):
        if value not in unique_pairs.values():
            unique_pairs[key] = value

    return unique_pairs
