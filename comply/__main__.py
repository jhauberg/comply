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

from comply import VERSION_PATTERN, is_compatible, allow_unicode
from comply.reporter import Reporter, XcodeReporter
from comply.checker import check
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


def compliance(files: int, files_total: int, violations: int) -> float:
    if files == 0 or violations == 0:
        return 1.0

    f = files  # files with violations

    min_f = 0
    max_f = files_total

    v = violations  # total violations

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
    if reporting_mode == 'standard':
        return Reporter(reports_solutions=True)
    elif reporting_mode == 'xcode':
        return XcodeReporter()

    return Reporter()


def make_rules() -> list:
    return [
        includes.ListNeededSymbols(),
        includes.SymbolListedNotNeeded(),
        includes.SymbolNeededNotListed(),
        includes.IncludeGuard(),
        includes.NoHeadersHeader(),
        misc.LineTooLong(),
        misc.FileTooLong()
    ]


def make_report(inputs: list, rules: list, reporter: Reporter):
    violations = 0
    files = 0
    files_with_violations = 0

    for path in inputs:
        result = check(path, rules, reporter)

        if result.checked:
            files += result.files
            files_with_violations += result.files_with_violations
            violations += result.violations

    if not isinstance(reporter, XcodeReporter):
        print('{0}/{1} files resulted in {2} violations'
              .format(files_with_violations, files, violations))

        if allow_unicode():
            print('compliance score: {0:.2f} ⚑'
                  .format(compliance(files_with_violations, files, violations)))
        else:
            print('compliance score: {0:.2f}'
                  .format(compliance(files_with_violations, files, violations)))

        print('finished')


def main():
    """ Entry point for invoking the comply module. """

    if not is_compatible():
        sys.exit('Python 3.5 or newer is required for running comply')

    arguments = docopt(__doc__, version='comply ' + __version__)

    check_for_update()

    rules = make_rules()

    inputs = arguments['<input>']

    reporting_mode = arguments['--reporter']
    reporter = make_reporter(reporting_mode)

    make_report(inputs, rules, reporter)


if __name__ == '__main__':
    main()
