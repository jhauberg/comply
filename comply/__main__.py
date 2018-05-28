#!/usr/bin/env python
# coding=utf-8

"""
Make your C follow the rules

Usage:
  comply <input>... [--reporter=<name>] [--check=<rule>]... [--except=<rule>]...
                    [--limit=<amount>] [--strict] [--only-severe] [--verbose]
                    [--profile]

  comply -h | --help
  comply --version

Options:
  -r --reporter=<name>    Specify type of reported output [default: human]
  -C --check=<rule>       Only run checks for specific rules
  -E --except=<rule>      Don't run checks for specific rules
  -i --limit=<amount>     Limit the amount of reported violations
  -s --strict             Report all violations (and don't suppress similar ones)
  -e --only-severe        Report only severe violations
  -P --profile            Show profiling/benchmark results
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
    EXIT_CODE_SUCCESS, EXIT_CODE_SUCCESS_WITH_SEVERE_VIOLATIONS,
    exit_if_not_compatible
)

from comply.reporting import Reporter, OneLineReporter, HumanReporter
from comply.printing import printdiag, diagnostics, supports_unicode, is_windows_environment
from comply.checking import check
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
                    printdiag('A newer version is available ({0})'.format(
                        remote_version_identifier))
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


def validate_names(names: list, rules: list):
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


def filter_rules(names: list, exceptions: list, severities: list) -> list:
    """ Return a list of rules to run checks on. """

    rulesets = [comply.rules.standard,
                comply.rules.experimental]

    all_rules = make_rules(rulesets)

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


def make_reporter(reporting_mode: str) -> Reporter:
    """ Return a reporter appropriate for the mode. """

    if reporting_mode == 'human':
        return HumanReporter()
    elif reporting_mode == 'oneline':
        return OneLineReporter()

    printdiag('Reporting mode \'{0}\' not available.'.format(reporting_mode),
              as_error=True)

    return Reporter()


def make_rules(modules: list) -> list:
    """ Return a list of instances of all Rule-subclasses found in the provided modules. """

    classes = []

    def is_rule_implementation(cls):
        """ Determine whether a class is a Rule implementation. """

        return cls != Rule and type(cls) == type and issubclass(cls, Rule)

    for module in modules:
        for item in dir(module):
            attr = getattr(module, item)

            if is_rule_implementation(attr):
                classes.append(attr)

    instances = [c() for c in classes]

    return instances


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

    if enable_profiling:
        printdiag('Profiling is enabled; --verbose was set automatically')

    is_strict = arguments['--strict']
    only_severe = arguments['--only-severe']

    checks = expand_params(arguments['--check'])
    exceptions = expand_params(arguments['--except'])

    severities = ([RuleViolation.DENY] if only_severe else
                  ([RuleViolation.DENY, RuleViolation.WARN] if not is_strict else
                   [RuleViolation.DENY, RuleViolation.WARN, RuleViolation.ALLOW]))

    rules = filter_rules(checks, exceptions, severities)

    reporting_mode = arguments['--reporter']

    reporter = make_reporter(reporting_mode)
    reporter.suppress_similar = not is_strict
    reporter.is_verbose = True if enable_profiling else arguments['--verbose']

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
        # note the whitespace; important for the full format later on
        severe_format = '({0} severe) ' if report.num_severe_violations > 0 else ''
        severe_format = severe_format.format(report.num_severe_violations)

        total_violations = report.num_violations + report.num_severe_violations

        violations_grammar = 'violation' if total_violations == 1 else 'violations'

        files_format = '{1}/{0}' if report.num_files_with_violations > 0 else '{0}'
        files_format = files_format.format(report.num_files, report.num_files_with_violations)

        # again, note the whitespace- it's intended
        use_strict_format = (' (set `--strict` to dig deeper)'
                             if not is_strict and total_violations == 0
                             else '')

        printdiag('Found {num_violations} {violations} {severe}'
                  'in {files} files'
                  '{use_strict}'
                  .format(num_violations=total_violations,
                          violations=violations_grammar,
                          severe=severe_format,
                          files=files_format,
                          use_strict=use_strict_format))

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
