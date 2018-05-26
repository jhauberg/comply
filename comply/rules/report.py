# coding=utf-8

from typing import List, Tuple


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
        self._original_lines = None

    def line_number_at(self, index: int, at_beginning: bool=False) -> (int, int):
        """ Return the line number and column at which a character index occur in the original text.

            Column is set to 1 if at_beginning is True.
        """

        return CheckFile.line_number_in_text(index, self.original, at_beginning)

    @staticmethod
    def line_number_at_start_of(line_index: int) -> (int, int):
        """ Return the line number and column at a given line index. """

        return line_index + 1, 1

    def line_number_at_top(self) -> (int, int):
        """ Return the line number and column at the top of a text. """

        return self.line_number_at(0, at_beginning=True)

    def lines_in(self, character_indices: (int, int)) -> List[Tuple[int, str]]:
        """ Return the lines and line numbers within starting and ending character indices. """

        starting, ending = character_indices

        starting_line_number, _ = self.line_number_at(starting)
        ending_line_number, _ = self.line_number_at(ending)

        all_lines = self.lines

        lines_in_range = []

        if ending_line_number > starting_line_number:
            for line_number in range(starting_line_number, ending_line_number + 1):
                lines_in_range.append((line_number,
                                       all_lines[line_number - 1]))
        else:
            lines_in_range.append((starting_line_number,
                                   all_lines[starting_line_number - 1]))

        return lines_in_range

    def lines_in_match(self, match) -> List[Tuple[int, str]]:
        """ Return the lines and line numbers of which the match spans. """

        character_range = (match.start(),
                           match.end())

        return self.lines_in(character_range)

    def line_at(self, line_number: int) -> str:
        """ Return the line at a line number, or None if line number is out of bounds.

            Note that a line number is *not* a zero-based index. The first line number is always 1.
        """

        line_index = line_number - 1

        if line_index < 0 or line_index > len(self.lines):
            return None

        return self.lines[line_number - 1]

    @property
    def lines(self):
        """ Return a list of lines from the original text. """

        if self._original_lines is None:
            self._original_lines = self.original.splitlines()

        return self._original_lines

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

    @staticmethod
    def line_number_in_text(index: int, text: str, at_beginning: bool=False) -> (int, int):
        """ Return the line number and column at which a character index occur in a text.

            Column is set to 1 if at_beginning is True.
        """

        line_index = text.count('\n', 0, index)

        if at_beginning:
            return CheckFile.line_number_at_start_of(line_index)

        column = index - text.rfind('\n', 0, index)

        return line_index + 1, column
