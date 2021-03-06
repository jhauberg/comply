#!/usr/bin/env python
# coding=utf-8

"""
Compliant Style Guide

Usage:
  comply <input>... [--reporter=<name>] [--check=<rule>]... [--except=<rule>]...
                    [--limit=<amount>] [--strict] [--only-severe] [--verbose]
                    [--profile]

  comply -h | --help
  comply --version

Options:
  -r --reporter=<name>    Specify type of reported output [default: human]
  -i --limit=<amount>     Limit the amount of reported violations
  -s --strict             Increase severity for less severe rules
  -P --profile            Show profiling/benchmark results
  -v --verbose            Show diagnostic messages
  -h --help               Show program help
  --version               Show program version

Options (non-compliant):
  -e --only-severe        Only run checks for rules of high severity
  -I --check=<rule>       Only run checks for specific rules
  -E --except=<rule>      Don't run checks for specific rules
"""

import os
import re
import sys
import datetime

from docopt import docopt

from pkg_resources import parse_version

from comply import (
    VERSION_PATTERN,
    EXIT_CODE_SUCCESS, EXIT_CODE_SUCCESS_WITH_SEVERE_VIOLATIONS,
    exit_if_not_compatible
)

from comply.reporting import Reporter, OneLineReporter, HumanReporter, XcodeReporter
from comply.printing import printdiag, diagnostics, supports_unicode, is_windows_environment, Colors
from comply.checking import find_checkable_files, check
from comply.version import __version__

import comply.printing

from comply.rules.report import CheckResult
from comply.rules.rule import Rule, RuleViolation
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
                    printdiag(Colors.GOOD +
                              'A newer version is available ({0})'.format(
                                  remote_version_identifier) +
                              Colors.RESET)
    except HTTPError:
        # fail silently
        pass
    except URLError:
        # fail silently
        pass


def expand_params(names: list) -> list:
    """ Return an expanded list of parameters from a list of comma-separated parameters.

        E.g. given a list of ['a', 'b,c,d'], returns ['a', 'b', 'c', 'd']
    """

    expanded_names = []

    for name in names:
        expanded_names.extend(
            [i.strip() for i in name.split(',')])

    return expanded_names


def print_invalid_names(names: list, rules: list):
    """ Go through and determine whether any of the provided names do not exist as named rules. """

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
    """ Determine whether a name corresponds to a named rule. """

    for rule in rules:
        if rule.name == name:
            return True

    return False


def filtered_rules(names: list, exceptions: list, severities: list) -> list:
    """ Return a list of rules to run checks on. """

    rulesets = [comply.rules.standard]

    rules = Rule.rules_in(rulesets)

    if len(names) > 0:
        print_invalid_names(names, rules)

        # filter out any rule not explicitly listed in --check
        rules = [rule for rule
                 in rules
                 if rule.name in names]

    # filter out any rule of unlisted severities
    rules = [rule for rule
             in rules
             if rule.severity in severities]

    if len(exceptions) > 0:
        print_invalid_names(exceptions, rules)

        # filter out rules explicitly listed in --except
        rules = [rule for rule
                 in rules
                 if rule.name not in exceptions]

    # sort rules in descending order, first by severity, then collection hint,
    # making sure severe violations are listed before less severe violations
    return sorted(rules,
                  reverse=True,
                  key=lambda rule: (rule.severity,
                                    rule.collection_hint))


def make_reporter(reporting_mode: str) -> Reporter:
    """ Return a reporter appropriate for the mode. """

    if reporting_mode == 'human':
        return HumanReporter()
    elif reporting_mode == 'oneline':
        return OneLineReporter()
    elif reporting_mode == 'xcode':
        return XcodeReporter()

    printdiag('Reporting mode \'{0}\' not available.'.format(reporting_mode),
              as_error=True)

    return Reporter()


def make_report(inputs: list, rules: list, reporter: Reporter) -> CheckResult:
    """ Run checks and print a report. """

    def not_checked(path: str, type: str, reason: str):
        """ Print a diagnostic stating when a file was not checked. """

        if reason is not None:
            printdiag('{type} \'{path}\' was not checked ({reason}).'.format(
                type=type, path=path, reason=reason))
        else:
            printdiag('{type} \'{path}\' was not checked.'.format(
                type=type, path=path))

    checkable_inputs = []

    # find all valid files from provided inputs
    for path in inputs:
        paths = find_checkable_files(path)

        if len(paths) > 0:
            # one or more valid files were found
            checkable_inputs.extend(paths)
        else:
            # no valid files were found in this path
            if os.path.isdir(path):
                # the path was a directory, but no valid files were found inside
                not_checked(path, type='Directory', reason='no files found')
            else:
                # the path was a single file, but not considered valid so it must not be supported
                not_checked(path, type='File', reason='file not supported')

    # sort paths for consistent output per identical run
    checkable_inputs = sorted(checkable_inputs)

    result = CheckResult()

    # set the total number of files we expect to report on
    reporter.files_total = len(checkable_inputs)

    # finally run the actual checks on each discovered file
    for path in checkable_inputs:
        file_result, checked = check(path, rules, reporter)

        if checked == CheckResult.FILE_CHECKED:
            # file was checked and results were reported if any
            result += file_result
        elif checked == CheckResult.FILE_SKIPPED:
            # file was fine but not checked (it should still count toward the total)
            result += file_result
        else:
            # file was not checked, for any number of reasons
            reason = None

            if checked == CheckResult.FILE_NOT_FOUND:
                reason = 'file not found'
            elif checked == CheckResult.FILE_NOT_READ:
                reason = 'file not read'

            not_checked(path, type='File', reason=reason)

    return result


def print_profiling_results(rules: list):
    """ Print benchmarking results/time taken for each rule. """

    num_rules_profiled = 0

    for rule in rules:
        time_taken = rule.total_time_spent_collecting

        if time_taken >= 0.1:
            printdiag(' [{0}] took {1:.1f} seconds'.format(
                rule.name, rule.total_time_spent_collecting))

            num_rules_profiled += 1

    num_rules_not_profiled = len(rules) - num_rules_profiled

    if num_rules_not_profiled > 0:
        printdiag(' (...{0} rules took nearly no time and were not shown)'.format(
            num_rules_not_profiled))


def print_rules_checked(rules: list, since_starting):
    """ Print the number of rules checked and time taken. """

    time_since_report = datetime.datetime.now() - since_starting
    report_in_seconds = time_since_report / datetime.timedelta(seconds=1)

    total_time_taken = report_in_seconds

    num_rules = len(rules)

    rules_grammar = 'rule' if num_rules == 1 else 'rules'

    printdiag('Checked {0} {1} in {2:.1f} seconds'.format(
        num_rules, rules_grammar, total_time_taken))


def print_report(report: CheckResult):
    """ Print the number of violations found in a report. """

    # note the whitespace; important for the full format later on
    severe_format = '({0} severe) ' if report.num_severe_violations > 0 else ''
    severe_format = severe_format.format(report.num_severe_violations)

    total_violations = report.num_violations + report.num_severe_violations

    violations_grammar = 'violation' if total_violations == 1 else 'violations'

    files_format = '{1}/{0}' if report.num_files_with_violations > 0 else '{0}'
    files_format = files_format.format(report.num_files, report.num_files_with_violations)

    printdiag('Found {num_violations} {violations} {severe}'
              'in {files} files'
              .format(num_violations=total_violations,
                      violations=violations_grammar,
                      severe=severe_format,
                      files=files_format))


def main():
    """ Entry point for invoking the comply module. """

    exit_if_not_compatible()

    if comply.PROFILING_IS_ENABLED:
        printdiag(('Profiling is enabled by default; '
                   'profiling should only be enabled through --profile or for debugging purposes'),
                  as_error=True)

    if not supports_unicode():
        if not is_windows_environment():
            # do not warn about this on Windows, as it probably won't work anyway
            printdiag('Unsupported shell encoding \'{0}\'. '
                      'Set environment variable `PYTHONIOENCODING` as UTF-8:\n'
                      '\texport PYTHONIOENCODING=UTF-8'
                      .format(diagnostics.encoding),
                      as_error=True)

    arguments = docopt(__doc__, version='comply ' + __version__)

    enable_profiling = arguments['--profile']

    comply.PROFILING_IS_ENABLED = enable_profiling

    is_verbose = arguments['--verbose']

    if enable_profiling and not is_verbose:
        printdiag('Profiling is enabled; --verbose was set automatically')

        is_verbose = True

    is_strict = arguments['--strict']
    only_severe = arguments['--only-severe']
    checks = expand_params(arguments['--check'])
    exceptions = expand_params(arguments['--except'])

    severities = ([RuleViolation.DENY] if only_severe else
                  [RuleViolation.DENY, RuleViolation.WARN, RuleViolation.ALLOW])

    # remove potential duplicates
    checks = list(set(checks))
    exceptions = list(set(exceptions))

    rules = filtered_rules(checks, exceptions, severities)

    reporting_mode = arguments['--reporter']

    reporter = make_reporter(reporting_mode)
    reporter.suppress_similar = not is_strict
    reporter.is_strict = is_strict
    reporter.is_verbose = is_verbose

    if arguments['--limit'] is not None:
        reporter.limit = int(arguments['--limit'])

    if not comply.printing.results.isatty() and reporter.suppress_similar:
        # when piping output elsewhere, let it be known that some results might be suppressed
        printdiag('Suppressing similar violations; results may be omitted '
                  '(set `--strict` to show everything)')

    inputs = arguments['<input>']

    time_started_report = datetime.datetime.now()

    report = make_report(inputs, rules, reporter)

    should_emit_verbose_diagnostics = reporter.is_verbose and report.num_files > 0

    if should_emit_verbose_diagnostics:
        print_rules_checked(rules, since_starting=time_started_report)

    if comply.PROFILING_IS_ENABLED:
        print_profiling_results(rules)

    if should_emit_verbose_diagnostics:
        print_report(report)

    if report.num_severe_violations > 0:
        # everything went fine; severe violations were encountered
        sys.exit(EXIT_CODE_SUCCESS_WITH_SEVERE_VIOLATIONS)
    else:
        # everything went fine; violations might have been encountered
        sys.exit(EXIT_CODE_SUCCESS)


if __name__ == '__main__':
    # note that --profile does *not* cause PROFILING_IS_ENABLED to be True at this point!
    # a developer must explicitly set PROFILING_IS_ENABLED to True to enable cProfile runs
    # this allows users to run the included benchmarking utilities without also
    # incurring the heavy duty cProfile runner, which is only interesting for developers
    if comply.PROFILING_IS_ENABLED:
        import cProfile
        import pstats

        filename = 'comply-profiling'

        cProfile.run('main()', filename)

        p = pstats.Stats(filename)

        with open(filename, 'w') as file:
            p.stream = file
            p.sort_stats('time').print_stats(20)

        with open(filename) as file:
            s = file.read()

            print('\n' + ('=' * len(s.splitlines()[0])))
            print('Profiling results - ', end='')
            print(s)

        if os.path.exists(filename):
            os.remove(filename)
    else:
        # we don't want to run update checks when we're profiling
        check_for_update()

        main()
