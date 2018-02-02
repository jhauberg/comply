# coding=utf-8

import os

from collections import OrderedDict

import comply.printing

from comply.printing import printdiag, printout, supports_color
from comply.util import truncated, Ellipsize


class Reporter:
    def __init__(self, suppress_similar: bool=True, is_verbose: bool=False):
        self.suppress_similar = suppress_similar
        self.is_verbose = is_verbose

    def group_by_reason(self, violations):
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
                    printdiag('(...{0} more suppressed)'
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
                location = '{0}:'.format(
                    truncated(path, length=40, options=Ellipsize.options(at=Ellipsize.middle)))

                why = '{0} [{1}]'.format(reason, violation.which.name)
                solution = violation.which.solution(violation)


                bold = '\x1b[1m' if supports_color(comply.printing.results) else ''
                italic = '\x1b[3m' if supports_color(comply.printing.results) else ''
                clear = '\x1b[0m' if supports_color(comply.printing.results) else ''

                if len(violation.lines) > 0:
                    context = ''

                    for i, (linenumber, line) in enumerate(violation.lines):
                        context += '{0}\t{i}{1}{cl}'.format(linenumber, line, i=italic, cl=clear)

                        if i != len(violation.lines) - 1:
                            context += '\n'

                    output = '{0} {1}\n{2}\n{b}{3}{cl}'.format(location, why,
                                                               context,
                                                               solution,
                                                               b=bold, cl=clear)
                else:
                    output = '{0} {1}\n{b}{2}{cl}'.format(location, why, solution,
                                                          b=bold, cl=clear)

                results.append(output)

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
