# coding=utf-8

import os

from typing import List

from collections import OrderedDict

import comply.printing as printing

from comply.rules import RuleViolation
from comply.printing import printdiag, printout
from comply.util.truncation import truncated


class Reporter:
    """ Represents the default reporting mode.

        This is not typically used as an actual reporting mode, but instead
        provides the base functions for specialized reporting modes.
    """

    def __init__(self, suppress_similar: bool=True, limit: int=None, is_verbose: bool=False):
        self.suppress_similar = suppress_similar
        self.is_verbose = is_verbose
        self.limit = limit
        self.count = 0

    @staticmethod
    def group_by_reason(violations: List[RuleViolation]):
        """ Return an ordered dict with violations grouped by their reason. """

        grouped = OrderedDict()

        for violation in violations:
            reason = violation.which.reason(violation)

            if reason not in grouped:
                grouped[reason] = []

            grouped[reason].append(violation)

        return grouped

    def report_before_checking(self, path: str, encoding: str=None):
        """ Print a diagnostic before initiating a check on a given file. """

        if self.is_verbose:
            normalized_path = os.path.normpath(path)

            encoding = ' ({enc})'.format(
                enc=encoding.upper()) if encoding is not None else ''

            diag = 'Checking \'{path}\'{enc}... '.format(
                path=truncated(normalized_path),
                enc=encoding)

            printdiag(diag, end='')

    def report_before_results(self, violations: List[RuleViolation]):
        """ Print a diagnostic before reporting results.

            This diagnostic should indicate the total number of violations collected; not
            the number of results to print (some may be suppressed).
        """

        if self.is_verbose:
            count = len(violations)

            violation_or_violations = 'violation' if count == 1 else 'violations'

            diag = 'Found {0} {1}'.format(
                count, violation_or_violations)

            printdiag(diag)

    def report_results(self, results: List[str], prefix_if_suppressed: str= '') -> int:
        """ Print each result (a formatted violation), suppressing similar results if needed. """

        emitted = 0

        for result in results:
            if self.limit is not None and self.count >= self.limit:
                break

            printout(result)

            emitted += 1

            self.count += 1

            # assuming each result is a violation "almost" identical to the rest
            if self.suppress_similar and emitted >= self.suppress_after:
                remaining = len(results) - emitted

                # if results are being piped or redirected, we don't need to emit a diagnostic
                # note that the PyCharm bit is just for testing purposes
                should_notify = printing.results.isatty() or 'PYCHARM' in os.environ

                if remaining > 0 and should_notify:
                    # note that this does not require --verbose;
                    # when a suppression occurs it should always be mentioned
                    printdiag('{0}(...{1} more suppressed)'
                              .format(prefix_if_suppressed, remaining))

                break

        return emitted

    def report(self, violations: list, path: str):
        """ Print a report of collected violations for a given file. """

        results = ['{0}: {1}'.format(path, violation) for violation in violations]

        self.report_results(results)

    @property
    def suppress_after(self) -> int:
        """ Return the number of similar violations emitted before being suppressed. """

        return 1
