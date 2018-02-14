#!/usr/bin/env python
# coding=utf-8

"""
Make your C follow the rules

Usage:
  comply <input>... [--reporter=<name>] [--check=<rule>]... [--except=<rule>]...
                    [--limit=<amount>] [--verbose] [--strict]
  comply -h | --help
  comply --version

Options:
  -r --reporter=<name>    Specify type of reported output [default: human]
  -c --check=<rule>       Only run checks for a specific rule
  -e --except=<rule>      Don't run checks for a specific rule
  -i --limit=<amount>     Limit the amount of reported violations
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

from comply.reporting import Reporter, OneLineReporter, HumanReporter
from comply.printing import printdiag, diagnostics, supports_unicode, is_windows_environment
from comply.checking import check, compliance, CheckResult
from comply.version import __version__

import comply.printing

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
                    printdiag('A newer version is available ({0})'.format(
                        remote_version_identifier))
    except HTTPError:
        # fail silently
        pass
    except URLError:
        # fail silently
        pass


def make_reporter(reporting_mode: str) -> Reporter:
    """ Return a reporter appropriate for the mode. """

    if reporting_mode == 'human':
        return HumanReporter()
    elif reporting_mode == 'oneline':
        return OneLineReporter()

    printdiag('Reporting mode \'{0}\' not available.'.format(reporting_mode),
              as_error=True)

    return Reporter()


def make_rules(names: list, exceptions: list, is_strict: bool) -> list:
    """ Return a list of rules to run checks on. """

    rules = [
        headers.GuardHeader(),
        headers.NoHeadersInHeader(),
        includes.ListNeededSymbols(),
        includes.SymbolListedNotNeeded(),
        includes.SymbolNeededNotListed(),
        includes.NoDuplicateIncludes(),
        functions.NoRedundantConst(),
        functions.TooManyParams(),
        functions.SplitByName(),
        functions.FunctionTooLong(),
        functions.TooManyFunctions(),
        functions.NoRedundantName(),
        functions.ConstOnRight(),
        functions.NoAttachedStars(),
        misc.IdentifierTooLong(),
        misc.TooManyBlanks(),
        misc.NoTabs(),
        misc.NoTodo(),
        misc.NoInvisibles(),
        misc.LineTooLong(),
        misc.FileTooLong(),
        misc.PreferStandardInt()
    ]

    if len(names) > 0:
        # only run checks for certain rules
        rules = [rule for rule
                 in rules
                 if rule.name in names]
    else:
        if not is_strict:
            # remove any rules of low severity
            rules = [rule for rule
                     in rules
                     if rule.severity > RuleViolation.ALLOW]

    if len(exceptions) > 0:
        # don't run checks for certain rules
        rules = [rule for rule
                 in rules
                 if rule.name not in exceptions]

    # sort rules in descending order, first by severity, then collection hint,
    # making sure severe violations are listed before less severe violations
    return sorted(rules, reverse=True, key=lambda rule: (rule.severity,
                                                         rule.collection_hint))


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
                      as_error=True)

    arguments = docopt(__doc__, version='comply ' + __version__)

    is_strict = arguments['--strict']

    checks = arguments['--check']
    exceptions = arguments['--except']

    rules = make_rules(checks, exceptions, is_strict)

    reporting_mode = arguments['--reporter']

    reporter = make_reporter(reporting_mode)
    reporter.suppress_similar = not is_strict
    reporter.is_verbose = arguments['--verbose']

    if arguments['--limit'] is not None:
        reporter.limit = int(arguments['--limit'])

    if not comply.printing.results.isatty() and reporter.suppress_similar:
        printdiag('Suppressing similar violations; results may be omitted '
                  '(set --strict to disable)')

    inputs = arguments['<input>']

    time_started_report = datetime.datetime.now()

    report = make_report(inputs, rules, reporter)

    if reporter.is_verbose:
        time_since_report = datetime.datetime.now() - time_started_report
        report_in_seconds = time_since_report / datetime.timedelta(seconds=1)

        total_time_taken = report_in_seconds

        if total_time_taken > 0.01:
            time_diagnostic = 'Analysis finished in {0:.1f} seconds'.format(
                total_time_taken)

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
