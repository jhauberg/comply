#!/usr/bin/env python
# coding=utf-8

"""
Make your C follow the rules

Usage:
  comply <input>...
  comply -h | --help

  comply --version

Options:
  -h --help    Show program help
  --version    Show program version
"""

import re

from docopt import docopt

from pkg_resources import parse_version

from comply import VERSION_PATTERN
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


def main():
    """ Entry point for invoking the comply module. """

    arguments = docopt(__doc__, version='comply ' + __version__)

    check_for_update()

    inputs = arguments['<input>']

    rules = [
        includes.ListSymbols(),
        includes.SymbolListedNotUsed(),
        includes.SymbolUsedNotListed(),
        misc.LineTooLong(),
        misc.FileTooLong()
    ]

    for path in inputs:
        check(path, rules)

    print('finished')


if __name__ == '__main__':
    main()
