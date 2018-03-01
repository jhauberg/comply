# coding=utf-8

import os

from typing import List

from comply.reporting import Reporter
from comply.rules import Rule, RuleViolation
from comply.util.stripping import strip_any_comments


class CheckResult:
    """ Represents the result of running a check on one or more files. """

    FILE_CHECKED = 1
    FILE_NOT_FOUND = -1
    NO_FILES_FOUND = -2
    FILE_NOT_SUPPORTED = -3

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


def check(path: str, rules: List[Rule], reporter: Reporter) -> (CheckResult, int):
    """ Run a check on the file found at path, if any.

        If the path points to a directory, a check is run on each subsequent filepath.

        Return a result and whether the path was checked.
    """

    result = CheckResult()

    if not os.path.exists(path):
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

    if extension not in supported_file_types():
        return result, CheckResult.FILE_NOT_SUPPORTED

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

        reporter.report_before_results(violations)

        if number_of_violations > 0:
            result.files_with_violations += 1

        reporter.report(violations, path)

    return result, CheckResult.FILE_CHECKED


def collect(text: str, filename: str, extension: str, rules: List[Rule]) -> List[RuleViolation]:
    """ Return a list of all collected violations in a text. """

    violations = []

    # remove block comments to reduce chance of false-positives for stuff that isn't actually code
    text_without_comments = strip_any_comments(text)

    for rule in rules:
        text_body = text if rule.expects_original_text else text_without_comments

        offenders = rule.collect(text_body, filename, extension)

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
