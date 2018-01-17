# coding=utf-8

import os

from comply.printer import print_offenders


def supported_file_types() -> tuple:
    """ Return all supported and recognized source filetypes. """

    return '.h', '.c'


def check(path: str, rules: list):
    """ Run a rules check on the file found at path, if any.

        If the path points to a directory, a check is run on each subsequent filepath.
    """

    if not os.path.exists(path):
        return

    if os.path.isdir(path):
        for file in os.listdir(path):
            filepath = os.path.join(path, file)

            check(filepath, rules)

        return

    filename, extension = os.path.splitext(path)

    if extension not in supported_file_types():
        return

    print('checking \'{0}\''.format(path))

    with open(path) as file:
        text = file.read()

        for rule in rules:
            offenders = rule.collect(text)

            print_offenders(offenders, path)
