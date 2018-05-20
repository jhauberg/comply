# coding=utf-8

import os

from typing import List

from comply import PROFILING_IS_ENABLED
from comply.reporting import Reporter
from comply.rules.rule import Rule, RuleViolation
from comply.rules.report import CheckFile, CheckResult

from comply.util.stripping import strip_any_comments, strip_any_literals

DEFAULT_ENCODING = 'utf8'


def supported_file_types() -> tuple:
    """ Return all supported and recognized source filetypes. """

    return '.h', '.c'


def result_from_violations(violations: List[RuleViolation]) -> CheckResult:
    """ Increment violation/file counts for a result. """

    result = CheckResult(violations)

    num_severe_violations = 0

    for violation in violations:
        if violation.which.severity == RuleViolation.DENY:
            num_severe_violations = 1

    num_violations = len(violations) - num_severe_violations

    result.num_files = 1
    result.num_violations = num_violations
    result.num_severe_violations = num_severe_violations

    if num_violations > 0 or num_severe_violations > 0:
        result.num_files_with_violations = 1

    return result


def check_text(text: str, rules: List[Rule]) -> CheckResult:
    """ Run a check on a piece of text. """

    file = prepare(text, 'N/A', 'N/A', 'N/A')

    violations = collect(file, rules)

    result = result_from_violations(violations)

    return result


def check(path: str, rules: List[Rule], reporter: Reporter=None) -> (CheckResult, int):
    """ Run a check on the file found at path, if any.

        If the path points to a directory, a check is run on each subsequent filepath.

        Return a result and a code to determine whether the path was checked or not.
    """

    result = CheckResult()

    if path is None or len(path) == 0 or not os.path.exists(path):
        return result, CheckResult.FILE_NOT_FOUND

    if os.path.isdir(path):
        checked_any = False

        for file in os.listdir(path):
            filepath = os.path.join(path, file)

            file_result, checked = check(filepath, rules, reporter)

            if checked == CheckResult.FILE_CHECKED:
                checked_any = True

                result += file_result

        return result, (CheckResult.FILE_CHECKED if checked_any else
                        CheckResult.NO_FILES_FOUND)

    filename, extension = os.path.splitext(path)

    extension = extension.lower()

    if extension not in supported_file_types():
        return result, CheckResult.FILE_NOT_SUPPORTED

    filename = os.path.basename(filename)

    text, encoding = read(path)

    if text is None:
        return result, CheckResult.FILE_NOT_READ

    if reporter is not None:
        reporter.report_before_checking(
            path, encoding=None if encoding is DEFAULT_ENCODING else encoding)

    file = prepare(text, filename, extension, path)

    violations = collect(file, rules, reporter.report_progress)

    result = result_from_violations(violations)

    if reporter is not None:
        reporter.report_before_results(violations)
        reporter.report(violations, path)

    return result, CheckResult.FILE_CHECKED


def prepare(text: str, filename: str, extension: str, path: str) -> CheckFile:
    """ Prepare a text for checking. """

    stripped_text = text

    # remove comments and string literals to reduce chance of false-positives
    # for stuff that isn't actually code
    # start by stripping single-line literals; this will help stripping comments, as
    # comment-starting characters could easily be found inside literals
    stripped_text = strip_any_literals(stripped_text)
    # finally strip both block and line-comments
    stripped_text = strip_any_comments(stripped_text)

    # debug code for comparing differences before/after stripping
    write_stripped_file = False

    if write_stripped_file:
        stripped_file_path = path + '.stripped'

        with open(stripped_file_path, 'w') as stripped_file:
            stripped_file.write(stripped_text)

    return CheckFile(text, stripped_text, filename, extension)


def read(path: str) -> (str, str):
    """ Return text and encoding used to read from file found at path.

        Return None if file could not be read with any supported encoding.
    """

    supported_encodings = [
        DEFAULT_ENCODING,
        'cp1252'
    ]

    for encoding in supported_encodings:
        try:
            with open(path, 'r', encoding=encoding) as file:
                text = file.read()

                return text, encoding
        except UnicodeDecodeError:
            pass

    return None, None


def collect(file: CheckFile, rules: List[Rule], progress_callback=None) -> List[RuleViolation]:
    """ Return a list of all collected violations in a text. """

    violations = []

    for i, rule in enumerate(rules):
        if PROFILING_IS_ENABLED:
            rule.profile_begin()

        offenders = rule.collect(file)

        if PROFILING_IS_ENABLED:
            rule.profile_end()

        violations.extend(offenders)

        if progress_callback is not None:
            progress_callback(i + 1, len(rules))

    return violations
