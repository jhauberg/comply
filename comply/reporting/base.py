# coding=utf-8

"""
Provides the base-class for reporting implementations.
"""

import os
import math

from typing import List

from collections import OrderedDict

import comply.printing as printing

from comply.rules.rule import RuleViolation
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
        self.reports = 0

    def report_before_checking(self, path: str, encoding: str=None):
        """ Print a diagnostic before initiating a check on a given file. """

        if self.is_verbose:
            normalized_path = os.path.normpath(path)

            encoding = ' ({enc})'.format(
                enc=encoding.upper()) if encoding is not None else ''

            diag = 'Checking \'{path}\'{enc}'.format(
                path=truncated(normalized_path),
                enc=encoding)

            printdiag(diag, end='')

    def report_progress(self, count, total):
        """ Print a progress indication. """

        if not self.is_verbose:
            return

        number_of_ticks = Reporter.determine_progress_ticks(count, total)

        printdiag('.' * number_of_ticks, end='')

    def report_before_results(self, violations: List[RuleViolation]):
        """ Print a diagnostic before reporting results.

            This diagnostic should indicate the total number of violations collected; not
            the number of results to print (some may be suppressed).
        """

        if not self.is_verbose:
            return

        count = len(violations)

        violation_or_violations = 'violation' if count == 1 else 'violations'

        diag = ' Found {0} {1}'.format(
            count, violation_or_violations)

        printdiag(diag)

    def report_results(self, results: List[str], prefix_if_suppressed: str= '') -> int:
        """ Print each result (a formatted violation), suppressing similar results if needed. """

        emitted = 0

        for result in results:
            printout(result)

            emitted += 1

            # assuming each result is a violation "almost" identical to the rest
            if self.suppress_similar and emitted >= self.suppresses_after:
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

    def report(self, violations: List[RuleViolation], path: str):
        """ Print a report of collected violations for a given file. """

        results = ['{0}: {1}'.format(path, violation) for violation in violations]

        self.report_results(results)

    @property
    def has_reached_reporting_limit(self) -> bool:
        """ Determine whether the specified limit of reports has been reached. """

        return self.limit is not None and self.reports == self.limit

    @property
    def suppresses_after(self) -> int:
        """ Return the number of similar violations emitted before being suppressed. """

        return 1

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

    @staticmethod
    def determine_progress_ticks(count, total, number_of_ticks=3) -> int:
        """ Determine the amount of progress indicator dots to print. """

        if total < number_of_ticks:
            # there's less rules than number of ticks,
            # so we will have to indicate increased progress for some ticks
            interval = number_of_ticks / total

            if count == total:
                # make last progress biased toward more ticks if necessary
                interval = math.ceil(interval)

            return int(interval)

        # determine the amount of rules to pass before indicating a tick in progress
        interval = math.floor(total / number_of_ticks)
        # determine the remaining rules until indicating a tick
        interval_remainder = count % interval

        if interval_remainder == 0:
            return 1

        return 0
