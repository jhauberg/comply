#!/usr/bin/env python
# coding=utf-8

"""
Make your C follow the rules

Usage:
  comply <input>... [--reporter=<name>] [--check=<rule>]... [--except=<rule>]...
                    [--limit=<amount>] [--strict] [--only-severe] [--verbose]
  comply -h | --help
  comply --version

Options:
  -r --reporter=<name>    Specify type of reported output [default: human]
  -c --check=<rule>       Only run checks for a specific rule
  -e --except=<rule>      Don't run checks for a specific rule
  -i --limit=<amount>     Limit the amount of reported violations
  -s --strict             Report all violations (and don't suppress similar ones)
  -S --only-severe        Report only severe violations
  -v --verbose            Show diagnostic messages
  -h --help               Show program help
  --version               Show program version
"""

import os
import re
import sys
import datetime

from docopt import docopt

from pkg_resources import parse_version

from comply import (
    VERSION_PATTERN,
    EXIT_CODE_SUCCESS, EXIT_CODE_SUCCESS_WITH_SEVERE_VIOLATIONS, exit_if_not_compatible
)

from comply.reporting import Reporter, OneLineReporter, HumanReporter
from comply.printing import printdiag, diagnostics, supports_unicode, is_windows_environment
from comply.checking import check
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


def validate_names(names: list, rules: list):
    """ Determine whether or not the provided names exist as named rules. """

    for name in names:
        if not is_name_valid(name, rules):
            # attempt fixing the name to provide a suggestion
            suggested_name = name.replace('_', '-').replace(' ', '-')

            if is_name_valid(suggested_name, rules):
                printdiag('Rule \'{rule}\' does not exist. Did you mean \'{suggestion}\'?'.format(
                    rule=name, suggestion=suggested_name))
            else:
                printdiag('Rule \'{rule}\' does not exist.'.format(
                    rule=name))


def is_name_valid(name: str, rules: list) -> bool:
    """ Determine whether or not a name corresponds with a named rule. """

    for rule in rules:
        if rule.name == name:
            return True

    return False


def make_rules(names: list, exceptions: list, severities: list) -> list:
    """ Return a list of rules to run checks on. """

    all_rules = [
        headers.GuardHeader(),
        headers.NoHeadersInHeader(),
        headers.NoUnifiedHeaders(),
        includes.ListNeededSymbols(),
        includes.SymbolListedNotNeeded(),
        #  includes.SymbolNeededNotListed(),
        includes.NoDuplicateIncludes(),
        includes.NoSourceIncludes(),
        functions.NoRedundantConst(),
        functions.TooManyParams(),
        functions.SplitByName(),
        functions.FunctionTooLong(),
        functions.TooManyFunctions(),
        functions.NoRedundantName(),
        functions.NoRedundantSize(),
        functions.NoUnnamedInts(),
        functions.NoAmbiguousFunctions(),
        functions.ExplicitlyVoidFunctions(),
        misc.IdentifierTooLong(),
        misc.TooManyBlanks(),
        misc.NoTabs(),
        misc.NoTodo(),
        misc.NoInvisibles(),
        misc.LineTooLong(),
        misc.FileTooLong(),
        misc.PreferStandardInt(),
        misc.ScopeTooDeep(),
        misc.ConstOnRight(),
        misc.NoSpaceName(),
        misc.PadKeywords(),
        misc.PadPointerDeclarations(),
        misc.LogicalContinuation()
    ]

    rules = all_rules

    if len(names) > 0:
        validate_names(names, rules)

        # only run checks for certain rules
        # (note that --strict mode is overruled when --check has at least one rule)
        rules = [rule for rule
                 in rules
                 if rule.name in names]
    else:
        rules = [rule for rule
                 in rules
                 if rule.severity in severities]

    if len(exceptions) > 0:
        validate_names(exceptions, rules)

        # don't run checks for certain rules
        rules = [rule for rule
                 in rules
                 if rule.name not in exceptions]

    # sort rules in descending order, first by severity, then collection hint,
    # making sure severe violations are listed before less severe violations
    return sorted(rules,
                  reverse=True,
                  key=lambda rule: (rule.severity,
                                    rule.collection_hint))


def make_report(inputs: list, rules: list, reporter: Reporter) -> CheckResult:
    """ Run checks and print a report. """

    result = CheckResult()

    for path in inputs:
        file_result, checked = check(path, rules, reporter)

        if checked == CheckResult.FILE_CHECKED:
            result += file_result
        else:
            reason = None

            file_or_directory = 'File'

            if checked == CheckResult.FILE_NOT_FOUND:
                reason = 'file not found'
            elif checked == CheckResult.FILE_NOT_READ:
                reason = 'file not read'
            elif checked == CheckResult.NO_FILES_FOUND:
                reason = 'no files found'

                file_or_directory = 'Directory'
            elif checked == CheckResult.FILE_NOT_SUPPORTED:
                reason = 'file not supported'

            if reason is not None:
                printdiag('{type} \'{path}\' was not checked ({reason}).'.format(
                    type=file_or_directory, path=os.path.abspath(path), reason=reason))
            else:
                printdiag('{type} \'{path}\' was not checked.'.format(
                    type=file_or_directory, path=os.path.abspath(path)))

    return result


def expand_names(names: list) -> list:
    """ Return an expanded list of names from a list of (potentially) comma-separated names.

        E.g. given a list of ['a', 'b,c,d'], returns ['a', 'b', 'c', 'd']
    """

    expanded_names = []

    for name in names:
        expanded_names.extend(
            [i.strip() for i in name.split(',')])

    return expanded_names


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
    only_severe = arguments['--only-severe']

    checks = expand_names(arguments['--check'])
    exceptions = expand_names(arguments['--except'])

    severities = ([RuleViolation.DENY] if only_severe else
                  ([RuleViolation.DENY, RuleViolation.WARN] if not is_strict else
                   [RuleViolation.DENY, RuleViolation.WARN, RuleViolation.ALLOW]))

    rules = make_rules(checks, exceptions, severities)

    reporting_mode = arguments['--reporter']

    reporter = make_reporter(reporting_mode)
    reporter.suppress_similar = not is_strict
    reporter.is_verbose = arguments['--verbose']

    if arguments['--limit'] is not None:
        reporter.limit = int(arguments['--limit'])

    if not comply.printing.results.isatty() and reporter.suppress_similar:
        printdiag('Suppressing similar violations; results may be omitted '
                  '(set --strict to show everything)')

    inputs = arguments['<input>']

    time_started_report = datetime.datetime.now()

    report = make_report(inputs, rules, reporter)

    if reporter.is_verbose and report.num_files > 0:
        time_since_report = datetime.datetime.now() - time_started_report
        report_in_seconds = time_since_report / datetime.timedelta(seconds=1)

        total_time_taken = report_in_seconds

        num_rules = len(rules)

        rules_or_rule = 'rule' if num_rules == 1 else 'rules'

        printdiag('Checked {0} {1} in {2:.1f} seconds'.format(
            num_rules, rules_or_rule, total_time_taken))

        severe_format = '({0} severe) '.format(
            report.num_severe_violations) if report.num_severe_violations > 0 else ''

        total_violations = report.num_violations + report.num_severe_violations

        violation_or_violations = 'violation' if total_violations == 1 else 'violations'

        printdiag('Found {num_violations} {violations} {severe}'
                  'in {num_files_violated}/{num_files} files'
                  .format(num_files_violated=report.num_files_with_violations,
                          num_files=report.num_files,
                          num_violations=total_violations,
                          violations=violation_or_violations,
                          severe=severe_format))

    check_for_update()

    if report.num_severe_violations > 0:
        # everything went fine; severe violations were encountered
        sys.exit(EXIT_CODE_SUCCESS_WITH_SEVERE_VIOLATIONS)
    else:
        # everything went fine; violations might have been encountered
        sys.exit(EXIT_CODE_SUCCESS)


if __name__ == '__main__':
    main()
