# coding=utf-8


class Rule:
    """ Represents a single rule. """

    def __init__(self, name: str, description: str, suggestion: str=None):
        self.name = name
        self.description = description
        self.suggestion = suggestion

    def __str__(self):
        return '[{0}] {1}'.format(self.name, self.description)

    def offend(self, at: (int, int), offending_text: str, token: str = None) -> 'RuleOffender':
        """ Return a rule offender originating from a chunk of text.

            Can optionally be provided with a token of the text, if something in particular should stand out.
        """

        return RuleOffender(self, at, offending_text, token)

    def collect(self, text: str) -> list:
        """ Analyze a given text and return a list of any found rule offenders. """

        return []


class RuleOffender:
    """ Represents an occurence of a broken rule. """

    def __init__(self, which: Rule, where: (int, int), what: str, token: str=None):
        self.which = which
        self.where = where
        self.what = what
        self.token = token

    def __str__(self):
        message = '{0} -> {1} {2}'.format(self.which, self.where, self.what)

        fix = self.which.suggestion

        if fix is not None:
            message += '\n Fix: {0}'.format(fix.format(self.token))

        return message

    @staticmethod
    def where(text: str, index: int) -> (int, int):
        """ Return the linenumber and column that a character index occurs in a text. """

        line = text.count('\n', 0, index) + 1
        offset = index - text.rfind('\n', 0, index)

        return line, offset
