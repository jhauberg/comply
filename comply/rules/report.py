# coding=utf-8


class CheckResult:
    """ Represents the result of running a check on one or more files. """

    FILE_CHECKED = 1
    FILE_NOT_FOUND = -1
    FILE_NOT_SUPPORTED = -2
    FILE_NOT_READ = -3
    NO_FILES_FOUND = -4

    def __init__(self,
                 violations: list=list(),
                 num_files: int=0,
                 num_files_with_violations: int=0,
                 num_violations: int=0,
                 num_severe_violations: int=0):
        self.violations = violations
        self.num_files = num_files
        self.num_files_with_violations = num_files_with_violations
        self.num_violations = num_violations
        self.num_severe_violations = num_severe_violations

    def __iadd__(self, other: 'CheckResult'):
        self.num_files += other.num_files
        self.num_files_with_violations += other.num_files_with_violations
        self.num_violations += other.num_violations
        self.num_severe_violations += other.num_severe_violations

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

        self._stripped_collaped = None

    @property
    def collapsed(self):
        """ Return stripped text with collapsed function bodies.

            Note that this is a lazy-loading property.

            The text is only processed once and subsequently cached and returned immediately on
            future calls.
        """

        if self._stripped_collaped is None:
            from comply.util.stripping import strip_function_bodies
            
            self._stripped_collaped = strip_function_bodies(self.stripped)

        return self._stripped_collaped
