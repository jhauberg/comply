#!/usr/bin/env python
# coding=utf-8

"""
Setup script for comply.

https://github.com/jhauberg/comply

Copyright 2018 Jacob Hauberg Hansen.
License: MIT (see LICENSE)
"""

import sys
import re

from setuptools import setup


VERSION_PATTERN = r'^__version__ = [\'"]([^\'"]*)[\'"]'


def determine_version_or_exit() -> str:
    """ Determine version identifier or exit the program. """

    if sys.version_info < (3, 5):
        sys.exit('Python 3.5 or newer is required for running comply')

    with open('comply/version.py') as file:
        version_contents = file.read()
        version_match = re.search(VERSION_PATTERN, version_contents, re.M)

        if version_match:
            version = version_match.group(1)

            return version

    sys.exit('Version could not be determined')


VERSION_IDENTIFIER = determine_version_or_exit()


setup(
    name='comply',
    version=VERSION_IDENTIFIER,
    description='Make your C code follow the rules',
    long_description=open('README.md').read(),
    url='https://github.com/jhauberg/comply',
    download_url='https://github.com/jhauberg/comply/archive/master.zip',
    author='Jacob Hauberg Hansen',
    author_email='jacob.hauberg@gmail.com',
    license='MIT',
    packages=['comply'],
    include_package_data=True,
    platforms='any',
    install_requires=[
        'docopt==0.6.2'
    ],
    entry_points={
        'console_scripts': [
            'comply = comply.__main__:main',
        ],
    }
)
