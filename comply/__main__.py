#!/usr/bin/env python
# coding=utf-8

"""
Make your C follow the rules

Usage:
  comply <input>... [--reporter=<name>] [--verbose] [--strict]
  comply -h | --help
  comply --version

Options:
  -r --reporter=<name>    Specify type of reported output [default: standard]
  -s --strict             Show all violations (similar violations not suppressed)
  -v --verbose            Show diagnostic messages
  -h --help               Show program help
  --version               Show program version
"""

import re
import datetime

from docopt import docopt

from pkg_resources import parse_version

from comply import VERSION_PATTERN, exit_if_not_compatible
from comply.reporter import Reporter, StandardReporter, ClangReporter
from comply.printing import printdiag, diagnostics, supports_unicode, is_windows_environment
from comply.checker import check, CheckResult
from comply.version import __version__

from comply.rules import *


def check_for_update():
    """ Determine whether a newer version is available remotely. """

    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError

    url = 'https://raw.githubusercontent.com/jhauberg/comply/master/comply/version.py'

    try:
        # specify a very short timeout, as this is a non-essential feature
        # and should not stall program exit indefinitely
        with urlopen(url, timeout=5) as response:
            # we're certain this file is UTF8, so we'll decode it right away
            response_body = response.read().decode('utf8')
            # search for the version string
            matches = re.search(VERSION_PATTERN, response_body, re.M)

            if matches:
                # if found, grab it and compare to the current installation
                remote_version_identifier = matches.group(1)

                if parse_version(__version__) < parse_version(remote_version_identifier):
                    printdiag('A newer version is available ({0} > {1})'
                              .format(remote_version_identifier, __version__))
    except HTTPError:
        # fail silently
        pass
    except URLError:
        # fail silently
        pass


def compliance(result: CheckResult) -> float:
    """ Return the compliance score """

    f = result.files_with_violations
    v = result.violations

    if f == 0 or v == 0:
        return 1.0

    min_f = 0
    max_f = result.files

    min_v = 0
    max_v = v + f  # arbitrary max

    vp = (v - min_v) / (max_v - min_v)
    fp = (f - min_f) / (max_f - min_f)

    # weigh files heavier than violations;
    #  e.g. 100 violations in 1 file should score better than 100 violations over 2 files
    v_weight = 0.4
    f_weight = 0.6

    v_score = vp * v_weight
    f_score = fp * f_weight

    score = 1.0 - (v_score + f_score)

    return score


def make_reporter(reporting_mode: str) -> Reporter:
    """ Return a reporter appropriate for the mode. """

    if reporting_mode == 'standard':
        return StandardReporter()
    elif reporting_mode == 'clang':
        return ClangReporter()

    printdiag('Reporting mode \'{0}\' not available.'.format(reporting_mode),
              apply_prefix=True)

    return Reporter()


def make_rules() -> list:
    """ Return a list of rules to run checks on. """

    rules = [
        includes.ListNeededSymbols(),
        includes.SymbolListedNotNeeded(),
        includes.SymbolNeededNotListed(),
        includes.IncludeGuard(),
        includes.NoHeadersHeader(),
        misc.NoTabs(),
        misc.LineTooLong(),
        misc.FileTooLong()
    ]

    return sorted(rules, key=lambda rule: rule.collection_hint)


def make_report(inputs: list, rules: list, reporter: Reporter) -> CheckResult:
    """  Run checks and print a report. """

    report = CheckResult()

    for path in inputs:
        result, checked = check(path, rules, reporter)

        if checked:
            report += result

    return report


def main():
    """ Entry point for invoking the comply module. """

    exit_if_not_compatible()

    if not supports_unicode():
        if not is_windows_environment():
            # do not warn about this on Windows, as it probably won't work anyway
            printdiag('Unsupported shell encoding \'{0}\'. '
                      'Set environment variable PYTHONIOENCODING as UTF-8:\n'
                      '\texport PYTHONIOENCODING=UTF-8'
                      .format(diagnostics.encoding),
                      apply_prefix=True)

    time_started_boot = datetime.datetime.now()

    arguments = docopt(__doc__, version='comply ' + __version__)

    rules = make_rules()

    inputs = arguments['<input>']

    reporting_mode = arguments['--reporter']

    reporter = make_reporter(reporting_mode)
    reporter.suppress_similar = not arguments['--strict']
    reporter.is_verbose = arguments['--verbose']

    time_since_boot = datetime.datetime.now() - time_started_boot
    time_started_report = datetime.datetime.now()

    report = make_report(inputs, rules, reporter)

    if reporter.is_verbose:
        time_since_report = datetime.datetime.now() - time_started_report

        boot_in_seconds = time_since_boot / datetime.timedelta(seconds=1)
        report_in_seconds = time_since_report / datetime.timedelta(seconds=1)

        total_time_taken = boot_in_seconds + report_in_seconds

        if total_time_taken > 0.01:
            time_diagnostic = 'Analysis finished in {0:.1f} seconds'.format(
                total_time_taken)

            time_diagnostic += ' ({0:.2f}s to load rules, {1:.2f}s running checks)'.format(
                boot_in_seconds, report_in_seconds)

            printdiag(time_diagnostic)

        score = compliance(report)
        score_format = '{0:.2f} ⚑' if supports_unicode() else '{0:.2f}'

        score = score_format.format(score)

        printdiag('Found {2} violations in {0}/{1} files (scoring {3})'
                  .format(report.files_with_violations,
                          report.files,
                          report.violations,
                          score))

    check_for_update()


if __name__ == '__main__':
    main()
