# coding=utf-8

import os

from typing import List

from comply.reporting import Reporter
from comply.rules import Rule, RuleViolation, CheckFile, CheckResult

from comply.util.stripping import strip_any_comments, strip_literals

DEFAULT_ENCODING = 'utf8'


def supported_file_types() -> tuple:
    """ Return all supported and recognized source filetypes. """

    return '.h', '.c'


def increment(result: CheckResult, violations: List[RuleViolation]):
    """ Increment violation/file counts for a result. """

    num_severe_violations = 0

    for violation in violations:
        if violation.which.severity == RuleViolation.DENY:
            num_severe_violations += 1

    num_violations = len(violations) - num_severe_violations

    result.files += 1
    result.violations += num_violations
    result.severe_violations += num_severe_violations

    if num_violations > 0 or num_severe_violations > 0:
        result.files_with_violations += 1


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

    violations = collect(file, rules)

    increment(result, violations)

    if reporter is not None:
        reporter.report_before_results(violations)
        reporter.report(violations, path)

    return result, CheckResult.FILE_CHECKED


def prepare(text: str, filename: str, extension: str, path: str) -> CheckFile:
    """ Prepare a text for checking. """

    # remove comments and string literals to reduce chance of false-positives
    # for stuff that isn't actually code
    stripped_text = strip_any_comments(text)
    stripped_text = strip_literals(stripped_text)

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


def collect(file: CheckFile, rules: List[Rule]) -> List[RuleViolation]:
    """ Return a list of all collected violations in a text. """

    violations = []

    for rule in rules:
        offenders = rule.collect(file)

        violations.extend(offenders)

    return violations


def compliance(result: CheckResult) -> float:
    """ Return the compliance score for a full result (all files checked). """

    f = result.files_with_violations
    v = result.violations

    if f == 0 or v == 0:
        return 1.0

    min_f = 0
    max_f = result.files

    min_v = 0
    max_v = v + f  # arbitrary max

    vp = (v - min_v) / (max_v - min_v)
    fp = (f - min_f) / (max_f - min_f)

    # weigh files heavier than violations;
    #  e.g. 100 violations in 1 file should score better than 100 violations over 2 files
    v_weight = 0.4
    f_weight = 0.6

    v_score = vp * v_weight
    f_score = fp * f_weight

    score = 1.0 - (v_score + f_score)

    return score
