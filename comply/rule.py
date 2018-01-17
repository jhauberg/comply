# coding=utf-8


class Rule:
    """ Represents a single rule. """

    def __init__(self, name: str, description: str, suggestion: str=None):
        self.name = name
        self.description = description
        self.suggestion = suggestion

    def __str__(self):
        return '[{0}] {1}'.format(self.name, self.description)

    def representation(self, offender: 'RuleOffender' = None):
        """ Return a representation of this rule.

            Subclasses may override and implement special formatting in relation to an offender.
        """

        return str(self)

    def solution(self, offender: 'RuleOffender'=None):
        """ Return a solution for this rule.

            Subclasses may override and implement special formatting in relation to an offender.
        """

        return self.suggestion

    def offend(self, at: (int, int), offending_text: str, meta: dict = None) -> 'RuleOffender':
        """ Return a rule offender originating from a chunk of text. """

        return RuleOffender(self, at, offending_text, meta)

    def collect(self, text: str) -> list:
        """ Analyze a given text and return a list of any found rule offenders. """

        return []


class RuleOffender:
    """ Represents an occurence of a broken rule. """

    def __init__(self, which: Rule, where: (int, int), what: str, meta: dict = None):
        self.which = which
        self.where = where
        self.what = what
        self.meta = meta

    def __str__(self):
        rule_repr = self.which.representation(offender=self)

        return '{0} -> {1} {2}'.format(rule_repr, self.where, self.what)

    @staticmethod
    def where(text: str, index: int) -> (int, int):
        """ Return the linenumber and column that a character index occurs in a text. """

        line = text.count('\n', 0, index) + 1
        offset = index - text.rfind('\n', 0, index)

        return line, offset
