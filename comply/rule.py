# coding=utf-8


class Rule:
    """ Represents a single rule. """

    def __init__(self, name: str, description: str, suggestion: str=None):
        self.name = name
        self.description = description
        self.suggestion = suggestion

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

    def violate(self, at: (int, int), offending_text: str, meta: dict = None) -> 'RuleViolation':
        """ Return a rule offender originating from a chunk of text. """

        return RuleViolation(self, at, offending_text, meta)

    def collect(self, text: str) -> list:
        """ Analyze a given text and return a list of any found rule offenders. """

        return []


class RuleViolation:
    """ Represents an occurence of a violated rule. """

    def __init__(self, which: Rule, where: (int, int), what: str, meta: dict = None):
        self.which = which
        self.where = where
        self.what = what
        self.meta = meta

    @staticmethod
    def where(text: str, index: int) -> (int, int):
        """ Return the linenumber and column that a character index occurs in a text. """

        line = text.count('\n', 0, index) + 1
        offset = index - text.rfind('\n', 0, index)

        return line, offset
