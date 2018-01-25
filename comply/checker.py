# coding=utf-8

import os

from comply.reporter import Reporter


class CheckResult:
    def __init__(self, checked: bool,
                 files: int=0,
                 files_with_violations: int=0,
                 violations: int=0):
        self.checked = checked
        self.files = files
        self.files_with_violations = files_with_violations
        self.violations = violations


def supported_file_types() -> tuple:
    """ Return all supported and recognized source filetypes. """

    return '.h', '.c'


def check(path: str, rules: list, reporter: Reporter) -> CheckResult:
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

            file_result = check(filepath, rules, reporter)

            if file_result.checked:
                result.files += file_result.files
                result.files_with_violations += file_result.files_with_violations
                result.violations += file_result.violations

        return result

    filename, extension = os.path.splitext(path)

    if extension not in supported_file_types():
        return CheckResult(checked=False)

    filename = os.path.basename(filename)

    reporter.report_before_checking(path)

    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()

        violations = []

        for rule in rules:
            offenders = rule.collect(text, filename, extension)
            violations.extend(offenders)

        number_of_violations = len(violations)

        result.files += 1
        result.violations += number_of_violations

        if number_of_violations > 0:
            result.files_with_violations += 1

        reporter.report_before_reporting(violations)
        reporter.report(violations, path)

    return result
