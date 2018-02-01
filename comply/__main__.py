#!/usr/bin/env python
# coding=utf-8

"""
Make your C follow the rules

Usage:
  comply <input>... [--reporter=<name>]
  comply -h | --help
  comply --version

Options:
  -r --reporter=<name>    Specify type of reported output [default: standard]
  -h --help               Show program help
  --version               Show program version
"""

import re
import sys

from docopt import docopt

from pkg_resources import parse_version

from comply import VERSION_PATTERN, is_compatible, supports_unicode
from comply.reporter import Reporter, ClangReporter
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
                    print('A newer version is available ({0})'.format(remote_version_identifier))
                    # end with empty break
                    print()
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


def make_reporter(reporting_mode: str, warning_if_unavailable: bool=False) -> Reporter:
    """ Return a reporter appropriate for the mode. """

    if reporting_mode == 'standard':
        return Reporter(reports_solutions=True)
    elif reporting_mode == 'clang':
        return ClangReporter()

    if warning_if_unavailable:
        print('comply: reporting mode \'{0}\' not available. Defaulting to \'standard\'.'
              .format(reporting_mode))

    return Reporter()


def make_rules() -> list:
    """ Return a list of rules to run checks on. """

    rules = [
        includes.ListNeededSymbols(),
        includes.SymbolListedNotNeeded(),
        includes.SymbolNeededNotListed(),
        includes.IncludeGuard(),
        includes.NoHeadersHeader(),
        misc.LineTooLong(),
        misc.FileTooLong()
    ]

    return sorted(rules, key=lambda rule: rule.collection_hint)


def make_report(inputs: list, rules: list, reporter: Reporter):
    """  Run checks and print a report. """

    total = CheckResult()

    for path in inputs:
        result, checked = check(path, rules, reporter)

        if checked:
            total += result

    score = compliance(total)
    score_format = '{0:.2f} ⚑' if supports_unicode() else '{0:.2f}'

    score = score_format.format(score)

    print('Found {2} violations in {0}/{1} files ({3})'.format(
        total.files_with_violations, total.files, total.violations, score))


def main():
    """ Entry point for invoking the comply module. """

    if not is_compatible():
        sys.exit('Python 3.5 or newer is required for running comply')

    if supports_unicode() and sys.stdout.encoding != 'UTF-8':
        sys.exit('Unsupported shell encoding \'{0}\'. '
                 'Set environment variable PYTHONIOENCODING as UTF-8:\n'
                 '\texport PYTHONIOENCODING=UTF-8'
                 .format(sys.stdout.encoding))

    arguments = docopt(__doc__, version='comply ' + __version__)

    check_for_update()

    rules = make_rules()

    inputs = arguments['<input>']

    reporting_mode = arguments['--reporter']
    reporter = make_reporter(reporting_mode, warning_if_unavailable=True)

    make_report(inputs, rules, reporter)


if __name__ == '__main__':
    main()
