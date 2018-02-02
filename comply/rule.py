# coding=utf-8


class Rule:
    """ Represents a single rule. """

    def __init__(self, name: str, description: str, suggestion: str=None):
        self.name = name
        self.description = description
        self.suggestion = suggestion

    def __repr__(self):
        return '[{0}]'.format(self.name)

    def reason(self, offender: 'RuleViolation' = None):
        """ Return a reason for a violation of this rule.

            Subclasses may override and provide specific formatting in relation to a rule violation.
        """

        return self.description

    def solution(self, offender: 'RuleViolation' =None):
        """ Return a solution for this rule.

            Subclasses may override and provide specific formatting in relation to a rule violation.
        """

        return self.suggestion

    def violate(self, at: (int, int), offending_lines: list=list(), meta: dict = None) -> 'RuleViolation':
        """ Return a rule offender originating from a chunk of text. """

        return RuleViolation(self, at, offending_lines, meta)

    def collect(self, text: str, filename: str, extension: str) -> list:
        """ Analyze a given text and return a list of any found rule offenders. """

        return []

    @property
    def collection_hint(self) -> int:
        return RuleViolation.MANY_PER_FILE


class RuleViolation:
    """ Represents an occurence of a violated rule. """

    """ A hint to indicate that a violation typically only occur once per file. """
    ONCE_PER_FILE = 0
    """ A hint to indicate that a violation may occur more than once per file. """
    MANY_PER_FILE = 1

    def __init__(self, which: Rule, where: (int, int), lines: list, meta: dict = None):
        self.which = which
        self.where = where
        self.lines = lines
        self.meta = meta

    def __repr__(self):
        return '{0} at {1}'.format(self.which, self.lines)

    @staticmethod
    def where(text: str, index: int, at_beginning: bool=False) -> (int, int):
        """ Return the linenumber and column that a character index occurs in a text. """

        line = text.count('\n', 0, index) + 1

        if at_beginning:
            column = 0
        else:
            column = index - text.rfind('\n', 0, index)

        return line, column
