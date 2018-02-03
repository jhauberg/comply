# coding=utf-8

import os

from collections import OrderedDict

import comply.printing

from comply.printing import printdiag, printout, Colors
from comply.util import truncated, Ellipsize


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
            normalized_path = os.path.normpath(path)

            diag = 'Checking \'{0}\'... '.format(truncated(normalized_path))

            printdiag(diag, end='')

    def report_before_reporting(self, violations: list):
        if self.is_verbose:
            diag = 'Found {0} violations'.format(len(violations))

            printdiag(diag)

    def report_similar_results(self, results: list, prefix_if_suppressed: str=''):
        emitted = 0

        for result in results:
            printout(result)

            emitted += 1

            if self.suppress_similar and emitted >= self.suppress_after:
                remaining = len(results) - emitted

                # if results are being piped or redirected, we don't need to emit a diagnostic
                # todo: the better solution might be to just disable suppression entirely in this case
                #       this would have the benefit of automatically avoiding this conditional and
                #       remove confusion when not notifying (it might seem like results are "missing")
                should_notify = comply.printing.results.isatty()

                if remaining > 0 and should_notify:
                    # note that this does not require verbosity flag; if a suppression does occur,
                    # it should always be mentioned
                    printdiag('{0}(...{1} more suppressed)'
                              .format(prefix_if_suppressed, remaining))

                break

    def report(self, violations: list, path: str):
        printout('{0}: {1}'.format(path, violations))

    @property
    def suppress_after(self) -> int:
        return 2


class StandardReporter(Reporter):
    """ Provides violation output (including suggestions) formatted for human readers. """

    def report(self, violations: list, path: str):
        # determine absolute path of file
        absolute_path = os.path.abspath(path)

        path_length = 24

        # pad if necessary (path too short)
        padded_path = absolute_path.ljust(path_length)
        # truncate if too long
        truncated_path = truncated(padded_path,
                                   length=path_length,
                                   options=Ellipsize.options(at=Ellipsize.start))

        # group violations by reason so that we can suppress similar ones
        grouped = self.group_by_reason(violations)

        for reason, violations in grouped.items():
            results = []

            for violation in violations:
                location = Colors.vague + '{0}:'.format(truncated_path) + Colors.clear

                why = '{w}{0} {vague}[{1}]'.format(reason, violation.which.name,
                                                   w=Colors.warn,
                                                   vague=Colors.vague)
                why = why + Colors.clear

                solution = violation.which.solution(violation)

                if len(violation.lines) > 0:
                    context = ''

                    for i, (linenumber, line) in enumerate(violation.lines):
                        if linenumber is None:
                            linenumber = 0

                        line = line.expandtabs(4)

                        context += Colors.emphasis + str(linenumber) + Colors.clear
                        context += '\t{0}'.format(line)

                        if i != len(violation.lines) - 1:
                            context += '\n'

                    output = '{1} {0}\n{2}\n{strong}{3}'.format(why, location, context, solution,
                                                                strong=Colors.strong)
                else:
                    output = '{1} {0}\n{strong}{2}'.format(why, location, solution,
                                                           strong=Colors.strong)

                results.append('\n' + output + Colors.clear)

            self.report_similar_results(results, prefix_if_suppressed='\n')

        printout('')


class ClangReporter(Reporter):
    """ Provides violation output formatted in a Clang-like fashion. """

    def report(self, violations: list, path: str):
        absolute_path = os.path.abspath(path)

        # group violations by reason so that we can suppress similar ones
        grouped = self.group_by_reason(violations)

        for reason, violations in grouped.items():
            results = []

            for violation in violations:
                line, column = violation.where

                if column > 0:
                    location = '{0}:{1}:{2}:'.format(absolute_path, line, column)
                else:
                    location = '{0}:{1}:'.format(absolute_path, line)

                why = '{0} [{1}]'.format(reason, violation.which.name)
                output = '{0} warning: {1}'.format(location, why)

                results.append(output)

            self.report_similar_results(results)
