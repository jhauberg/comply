# coding=utf-8

import os.path

from comply.printer import print_offenders


def check(path: str, rules: list):
    """ Run a rules check on the file found at path.

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

    if ('.h' not in extension and
        '.c' not in extension):
        return

    print('checking \'{0}\''.format(path))

    with open(path) as file:
        text = file.read()

        for rule in rules:
            offenders = rule.collect(text)

            print_offenders(offenders)
