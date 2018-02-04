# coding=utf-8

import os

from comply.reporter import Reporter


class CheckResult:
    def __init__(self,
                 files: int=0,
                 files_with_violations: int=0,
                 violations: int=0):
        self.files = files
        self.files_with_violations = files_with_violations
        self.violations = violations

    def __iadd__(self, other):
        self.files += other.files
        self.files_with_violations += other.files_with_violations
        self.violations += other.violations

        return self


def supported_file_types() -> tuple:
    """ Return all supported and recognized source filetypes. """

    return '.h', '.c'


def check(path: str, rules: list, reporter: Reporter) -> (CheckResult, bool):
    """ Run a rules check on the file found at path, if any.

        If the path points to a directory, a check is run on each subsequent filepath.

        Return a result and whether the path was checked.
    """

    result = CheckResult()

    if not os.path.exists(path):
        return result, False

    if os.path.isdir(path):
        checked_any = False

        for file in os.listdir(path):
            filepath = os.path.join(path, file)

            file_result, checked = check(filepath, rules, reporter)

            if checked:
                checked_any = True

                result += file_result

        return result, checked_any

    filename, extension = os.path.splitext(path)

    if extension not in supported_file_types():
        return result, False

    filename = os.path.basename(filename)

    text = None

    default_encoding = 'utf-8'

    supported_encodings = [
        default_encoding,
        'windows-1252'
    ]

    for encoding in supported_encodings:
        try:
            with open(path, 'r', encoding=encoding) as file:
                text = file.read()
        except UnicodeDecodeError:
            pass
        else:
            reporter.report_before_checking(
                path, encoding=None if encoding is default_encoding else encoding)

            break

    if text is not None:
        violations = collect(text, filename, extension, rules)

        number_of_violations = len(violations)

        result.files += 1
        result.violations += number_of_violations

        reporter.report_before_reporting(violations)

        if number_of_violations > 0:
            result.files_with_violations += 1

            reporter.report(violations, path)

    return result, True


def collect(text: str, filename: str, extension: str, rules: list) -> list:
    violations = []

    for rule in rules:
        offenders = rule.collect(text, filename, extension)
        violations.extend(offenders)

    return violations
