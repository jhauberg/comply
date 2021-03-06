# coding=utf-8

"""
Models for dealing with checked files and their results.
"""

from typing import List, Tuple


class CheckResult:
    """ Represents the result of running a check on one or more files. """

    FILE_CHECKED = 1
    FILE_SKIPPED = 2
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

    def line_number_at(self, character_index: int, span_entire_line: bool=False) -> (int, int):
        """ Return the line number and column at which a character index occur. """

        return CheckFile.line_number_in_text(character_index, self.original, span_entire_line)

    def line_number_at_top(self) -> (int, int):
        """ Return the line number and column at the beginning of a text. """

        return self.line_number_at(0, span_entire_line=True)

    def lines_in_line_range(self, line_numbers: (int, int)) -> List[Tuple[int, str]]:
        """ Return the lines and line numbers in a range of line numbers. """

        all_lines = self.lines

        starting_line_number, ending_line_number = line_numbers

        lines_in_range = []

        if ending_line_number > starting_line_number:
            for line_number in range(starting_line_number, ending_line_number + 1):
                lines_in_range.append((line_number,
                                       all_lines[line_number - 1]))
        else:
            lines_in_range.append((starting_line_number,
                                   all_lines[starting_line_number - 1]))

        return lines_in_range

    def lines_in_character_range(self, characters: (int, int)) -> List[Tuple[int, str]]:
        """ Return the lines and line numbers that spans the starting and ending character
            indices.
        """

        starting, ending = characters

        starting_line_number, _ = self.line_number_at(starting)
        ending_line_number, _ = self.line_number_at(ending)

        return self.lines_in_line_range((starting_line_number, ending_line_number))

    def lines_in_match(self, match) -> List[Tuple[int, str]]:
        """ Return the lines and line numbers of which the match spans. """

        characters = (match.start(),
                      match.end())

        return self.lines_in_character_range(characters)

    def line_at(self, line_number: int) -> str:
        """ Return the line at a line number.

            Note that a line number is *not* a zero-based index. The first line number is always 1.
        """

        line_index = line_number - 1

        return self.lines[line_index]

    @property
    def lines(self):
        """ Return a list of lines from the original text. """

        if self._original_lines is None:
            self._original_lines = self.original.splitlines()

        return self._original_lines

    @staticmethod
    def line_number_in_text(character_index: int, text: str, span_entire_line: bool=False) -> (int, int):
        """ Return the line number and column at which a character index occur in a text.

            Column is set to 0 if span_entire_line is True.
        """

        line_index = text.count('\n', 0, character_index)

        if span_entire_line:
            return CheckFile.line_number_at_start_of(line_index, span_entire_line)

        column = character_index - text.rfind('\n', 0, character_index)

        return line_index + 1, column

    @staticmethod
    def line_number_at_start_of(line_index: int, span_entire_line: bool=False) -> (int, int):
        """ Return the line number and column at a given line index.

            Column is set to 0 if span_entire_line is True.
        """

        return line_index + 1, 0 if span_entire_line else 1

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
