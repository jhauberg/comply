# coding=utf-8

"""
Provides functions for preparing and checking source files.
"""

import os
import glob
import comply

from typing import List

from comply.reporting import Reporter
from comply.rules.rule import Rule, RuleViolation
from comply.rules.report import CheckFile, CheckResult

from comply.util.stripping import strip_any_comments, strip_any_literals

DEFAULT_ENCODING = 'utf8'


def supported_file_types() -> tuple:
    """ Return all supported and recognized source filetypes. """

    return '.h', '.c'


def find_checkable_files(path: str) -> list:
    """ Return a list of all checkable files found in a path.

        If path is a directory, traverse through it and any subdirectories to find checkable files.

        If path points to a non-supported file, it is *not* excluded.
    """

    supported_extensions = ''.join([extension[1:].lower() for extension in supported_file_types()])

    # match file with supported extension in dir and all subdirs
    pattern = '/**/*.[{extensions}]'.format(extensions=supported_extensions)

    checkable_paths = []

    if os.path.isdir(path):
        # input is a directory; traverse it and any subdirectories looking for supported files
        directory_pattern = path + pattern

        supported_filepaths = glob.glob(directory_pattern, recursive=True)

        checkable_paths.extend(supported_filepaths)
    else:
        # input is a plain filepath
        checkable_paths.append(path)

    # remove potential duplicates
    checkable_paths = list(set(checkable_paths))

    return checkable_paths


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


def check_text(text: str, rules: List[Rule], assumed_filename: str=None) -> CheckResult:
    """ Run a check on a piece of text. """

    path = assumed_filename

    filename, extension = os.path.splitext(path) if path is not None else (None, None)

    file = prepare(text, filename, extension, path)

    violations = collect(file, rules)

    result = result_from_violations(violations)

    return result


def check(path: str, rules: List[Rule], reporter: Reporter=None) -> (CheckResult, int):
    """ Run a check on the file found at path.

        Return a result and a code to determine whether the file was checked or not.
    """

    result = CheckResult()

    if (path is None
            or len(path) == 0
            or not os.path.exists(path)
            or not os.path.isfile(path)):
        return result, CheckResult.FILE_NOT_FOUND

    filename, extension = os.path.splitext(path)

    extension = extension.lower()

    if extension not in supported_file_types():
        return result, CheckResult.FILE_NOT_SUPPORTED

    filename = os.path.basename(filename)

    text, encoding = read(path)

    if text is None:
        return result, CheckResult.FILE_NOT_READ

    if reporter is not None:
        reporter.files_encountered += 1

        if reporter.has_reached_reporting_limit:
            result.num_files = 1

            return result, CheckResult.FILE_SKIPPED

        reporter.report_before_checking(
            path, encoding=None if encoding is DEFAULT_ENCODING else encoding)

    file = prepare(text, filename, extension, path)

    violations = collect(file, rules, reporter)

    result = result_from_violations(violations)

    if reporter is not None:
        reporter.report_before_results(violations)
        reporter.report(violations, path)

    return result, CheckResult.FILE_CHECKED


def prepare(text: str, filename: str, extension: str, path: str=None) -> CheckFile:
    """ Prepare a text for checking. """

    # remove form-feed characters to make sure line numbers are as expected
    original_text = text.replace('\u000c', '')

    stripped_text = original_text

    # remove comments and string literals to reduce chance of false-positives
    # for stuff that isn't actually code
    # start by stripping single-line literals; this will help stripping comments, as
    # comment-starting characters could easily be found inside literals
    stripped_text = strip_any_literals(stripped_text)
    # finally strip both block and line-comments
    stripped_text = strip_any_comments(stripped_text)

    # debug code for comparing differences before/after stripping
    write_stripped_file = False

    if write_stripped_file and path is not None:
        stripped_file_path = path + '.stripped'

        with open(stripped_file_path, 'w') as stripped_file:
            stripped_file.write(stripped_text)

    return CheckFile(original_text, stripped_text, filename, extension)


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


def collect(file: CheckFile, rules: List[Rule], reporter: Reporter=None) -> List[RuleViolation]:
    """ Return a list of all collected violations in a text. """

    violations = []

    for i, rule in enumerate(rules):
        if comply.PROFILING_IS_ENABLED:
            rule.profile_begin()

        offenders = rule.collect(file)

        if comply.PROFILING_IS_ENABLED:
            rule.profile_end()

        if reporter is not None and reporter.limit is not None:
            reporter.reports += len(offenders)

            if reporter.reports > reporter.limit:
                num_exceeding_reports = reporter.reports - reporter.limit
                reporter.reports = reporter.limit

                offenders = offenders[:-num_exceeding_reports]

        violations.extend(offenders)

        if reporter is not None:
            n = len(rules)

            if reporter.has_reached_reporting_limit:
                # pretend we're running the remaining iterations to get the proper
                # amount of progress indication ticks
                for j in range(i, n):
                    reporter.report_progress(j + 1, n)

                break

            reporter.report_progress(i + 1, n)

    return violations
