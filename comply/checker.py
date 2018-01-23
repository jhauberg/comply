# coding=utf-8

import os

from comply.printer import Printer


class CheckResult:
    def __init__(self, checked: bool, files: int=0, violations: int=0):
        self.checked = checked
        self.files = files
        self.violations = violations


def supported_file_types() -> tuple:
    """ Return all supported and recognized source filetypes. """

    return '.h', '.c'


def check(path: str, rules: list, printer: Printer) -> CheckResult:
    """ Run a rules check on the file found at path, if any.

        If the path points to a directory, a check is run on each subsequent filepath.

        Return whether the path was checked, how many files were checked (if recursed through a
        directory) and the number of violations encountered.
    """

    if not os.path.exists(path):
        return CheckResult(checked=False)

    result = CheckResult(checked=True)

    if os.path.isdir(path):
        for file in os.listdir(path):
            filepath = os.path.join(path, file)

            file_result = check(filepath, rules, printer)

            if file_result.checked:
                result.files += file_result.files
                result.violations += file_result.violations

        return result

    filename, extension = os.path.splitext(path)

    if extension not in supported_file_types():
        return CheckResult(checked=False)

    filename = os.path.basename(filename)

    printer.report_before_checking(path)

    with open(path) as file:
        text = file.read()

        violations = []

        for rule in rules:
            offenders = rule.collect(text, filename, extension)
            violations.extend(offenders)

        result.files += 1
        result.violations += len(violations)

        printer.report_before_reporting(violations)
        printer.report(violations, path)

    return result
