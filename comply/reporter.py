# coding=utf-8

import os

from collections import OrderedDict

from comply.printing import printdiag, printout, Colors
from comply.util import truncated


class Reporter:
    def __init__(self, suppress_similar: bool=True, is_verbose: bool=False):
        self.suppress_similar = suppress_similar
        self.is_verbose = is_verbose

    @staticmethod
    def group_by_reason(violations):
        """ Return an ordered dict with violations grouped by their reason. """

        grouped = OrderedDict()

        for violation in violations:
            reason = violation.which.reason(violation)

            if reason not in grouped:
                grouped[reason] = []

            grouped[reason].append(violation)

        return grouped

    def report_before_checking(self, path: str):
        if self.is_verbose:
            diag = 'Checking \'{0}\'... '.format(truncated(path))

            printdiag(diag, end='')

    def report_before_reporting(self, violations: list):
        if self.is_verbose:
            diag = 'Found {0} violations'.format(len(violations))

            printdiag(diag)

    def report_similar_results(self, results: list):
        emitted = 0

        for result in results:
            printout(result)

            emitted += 1

            if self.suppress_similar and emitted >= self.suppress_after:
                remaining = len(results) - emitted

                if remaining > 0:
                    # note that this does not require verbosity flag; if a suppression does occur,
                    # it should always be mentioned
                    printdiag('\n(...{0} more suppressed)'
                              .format(remaining))

                break

    def report(self, violations: list, path: str):
        printout('{0}: {1}'.format(path, violations))

    @property
    def suppress_after(self) -> int:
        return 2


class StandardReporter(Reporter):
    """ Provides violation output (including suggestions) formatted for human readers. """

    def report(self, violations: list, path: str):
        # group violations by reason so that we can suppress similar ones
        grouped = self.group_by_reason(violations)

        for reason, violations in grouped.items():
            results = []

            for violation in violations:
                location = Colors.vague + '{0}:'.format(path) + Colors.clear

                why = '{w}{0} {vague}[{1}]'.format(reason, violation.which.name,
                                                   w=Colors.warn,
                                                   vague=Colors.vague)
                why = why + Colors.clear

                solution = violation.which.solution(violation)

                if len(violation.lines) > 0:
                    context = ''

                    for i, (linenumber, line) in enumerate(violation.lines):
                        context += '{em}{0}{cl}\t{1}'.format(linenumber, line,
                                                             em=Colors.emphasis,
                                                             cl=Colors.clear)

                        if i != len(violation.lines) - 1:
                            context += '\n'

                    output = '{1}\n{0}\n{2}\n{strong}{3}'.format(location, why,
                                                                 context,
                                                                 solution,
                                                                 strong=Colors.strong)
                else:
                    output = '{1}\n{0}\n{strong}{2}'.format(location, why, solution,
                                                            strong=Colors.strong)

                results.append('\n' + output + Colors.clear)

            self.report_similar_results(results)

        printout('')


class ClangReporter(Reporter):
    """ Provides violation output formatted in a Clang-like fashion. """

    def report(self, violations: list, path: str):
        # group violations by reason so that we can suppress similar ones
        grouped = self.group_by_reason(violations)

        for reason, violations in grouped.items():
            results = []

            for violation in violations:
                absolute_path = os.path.abspath(path)

                line, column = violation.where

                if column > 0:
                    location = '{0}:{1}:{2}:'.format(absolute_path, line, column)
                else:
                    location = '{0}:{1}:'.format(absolute_path, line)

                why = '{0} [{1}]'.format(reason, violation.which.name)
                output = '{0} warning: {1}'.format(location, why)

                results.append(output)

            self.report_similar_results(results)
