# coding=utf-8

from typing import List, Tuple

from comply.rules.check import CheckFile


class RuleViolation:
    """ Represents an occurence of a rule violation. """

    """ A hint to indicate that a violation typically only occur once per file. """
    ONCE_PER_FILE = 1
    """ A hint to indicate that a violation may occur more than once per file. """
    MANY_PER_FILE = 0

    """ A severity indicator for violations that have a negative impact, but can't be objectively
        deemed to be an issue.
    """
    ALLOW = 0
    """ A severity indicator for violations that have an objectively negative impact.
    
        This is the default severity. 
    """
    WARN = 1
    """ A severity indicator for violations that have an objectively severe negative impact. """
    DENY = 2

    def __init__(self, which: 'Rule', where: (int, int), lines: List[Tuple[int, str]], meta: dict=None):
        self.which = which
        self.where = where
        self.lines = lines
        self.meta = meta

    def __repr__(self):
        return '{0} at {1}'.format(self.which, self.lines)

    def index_of_violating_line(self) -> int:
        """ Return the index of the line where this violation occurs.

            Note that the index *is not* the line number.
        """

        line_numbers = [line[0] for line in self.lines]

        return line_numbers.index(self.where[0])

    @staticmethod
    def at_top() -> (int, int):
        """ Return the line number and column at the top of a text. """

        return 1, 0

    @staticmethod
    def at(index: int, text: str, at_beginning: bool=False) -> (int, int):
        """ Return the line number and column at which a character index occur in a text.

            Column is set to 0 if at_beginning is True.
        """

        line = text.count('\n', 0, index) + 1

        if at_beginning:
            column = 0
        else:
            column = index - text.rfind('\n', 0, index)

        return line, column

    @staticmethod
    def lines_in(character_indices: (int, int), text: str) -> List[Tuple[int, str]]:
        """ Return the lines and line numbers within starting and ending character indices. """

        all_lines = text.splitlines()

        starting, ending = character_indices

        starting_line_number, _ = RuleViolation.at(starting, text)
        ending_line_number, _ = RuleViolation.at(ending, text)

        lines_in_range = []

        if ending_line_number > starting_line_number:
            for line_number in range(starting_line_number, ending_line_number + 1):
                lines_in_range.append((line_number,
                                       all_lines[line_number - 1]))
        else:
            lines_in_range.append((starting_line_number,
                                   all_lines[starting_line_number - 1]))

        return lines_in_range


class Rule:
    """ Represents a single rule. """

    def __init__(self, name: str, description: str, suggestion: str=None):
        self.name = name
        self.description = description
        self.suggestion = suggestion

    def __repr__(self):
        name = (self.name
                if self.name is not None
                else '<unnamed>')

        return '[{0}]'.format(name)

    def reason(self, violation: RuleViolation=None):
        """ Return a reason for why a given violation occurred.

            Base behavior is to format any associated meta information from the violation into
            the reason/description string as defined by the rule.

            Subclasses may override to provide customized formatting.
        """

        description = self.description

        if description is None or len(description) == 0:
            return description

        if violation.meta is None or len(violation.meta) == 0:
            return description

        return description.format(**violation.meta)

    def solution(self, violation: RuleViolation=None):
        """ Return a solution for fixing a given violation.

            Base behavior is to format any associated meta information from the violation into
            the solution/suggestion string as defined by the rule.

            Subclasses may override to provide customized formatting.
        """

        suggestion = self.suggestion

        if suggestion is None or len(suggestion) == 0:
            return suggestion

        if violation.meta is None or len(violation.meta) == 0:
            return suggestion

        return suggestion.format(**violation.meta)

    def augment(self, violation: RuleViolation):
        """ Augment a violation to improve hints of its occurrence.

            Subclasses may override and provide custom augments.
        """

        pass

    def violate(self, at: (int, int), lines: List[Tuple[int, str]]=list(), meta: dict=None) -> RuleViolation:
        """ Return a rule violation originating from a chunk of text. """

        return RuleViolation(self, at, lines, meta)

    def collect(self, file: CheckFile) -> List[RuleViolation]:
        """ Analyze a given text and return a list of any found violations.

            Subclasses should override and provide rule-specific collection logic.
        """

        return []

    @property
    def severity(self) -> int:
        """ Return a number indicating the severity of violating this rule. """

        return RuleViolation.WARN

    @property
    def collection_hint(self) -> int:
        """ Return a hint indicating how often this rule may be violated per file.

            For example, some rule violations can only occur once per file; others more than once.
        """

        return RuleViolation.MANY_PER_FILE

