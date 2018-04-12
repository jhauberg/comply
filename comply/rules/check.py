# coding=utf-8


class CheckResult:
    """ Represents the result of running a check on one or more files. """

    FILE_CHECKED = 1
    FILE_NOT_FOUND = -1
    FILE_NOT_SUPPORTED = -2
    FILE_NOT_READ = -3
    NO_FILES_FOUND = -4

    def __init__(self,
                 files: int=0,
                 files_with_violations: int=0,
                 violations: int=0,
                 severe_violations: int=0):
        self.files = files
        self.files_with_violations = files_with_violations
        self.violations = violations
        self.severe_violations = severe_violations

    def __iadd__(self, other):
        self.files += other.files
        self.files_with_violations += other.files_with_violations
        self.violations += other.violations
        self.severe_violations += other.severe_violations

        return self


class CheckFile:
    """ Represents a source file that has been prepared for checking. """

    def __init__(self,
                 original: str,
                 stripped: str,
                 filename: str,
                 extension: str):
        self.original = original
        self.stripped = stripped
        self.filename = filename
        self.extension = extension
