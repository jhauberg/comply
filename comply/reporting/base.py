# coding=utf-8

import os

from collections import OrderedDict

import comply.printing

from comply.printing import printdiag, printout
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

    def report_before_checking(self, path: str, encoding: str=None):
        if self.is_verbose:
            normalized_path = os.path.normpath(path)

            encoding = ' ({0})'.format(
                encoding.upper()) if encoding is not None else ''

            diag = 'Checking \'{0}\'{1}... '.format(
                truncated(normalized_path), encoding)

            printdiag(diag, end='')

    def report_before_reporting(self, violations: list):
        if self.is_verbose:
            count = len(violations)

            diag = 'Found {0} {1}'.format(
                count, 'violation' if count == 1 else 'violations')

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
