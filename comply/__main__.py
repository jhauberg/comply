#!/usr/bin/env python
# coding=utf-8

"""
Make your C follow the rules

Usage:
  comply -h | --help
  comply --version

Options:
  -h --help    Show program help
  --version    Show program version
"""

from docopt import docopt

from comply.version import __version__


def main():
    """ Entry point for invoking the comply module. """

    arguments = docopt(__doc__, version='comply ' + __version__)

    print(arguments)


if __name__ == '__main__':
    main()
