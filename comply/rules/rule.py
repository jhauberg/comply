# coding=utf-8

from typing import List, Tuple


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


class Rule:
    """ Represents a single rule. """

    def __init__(self, name: str, description: str, suggestion: str=None, expects_original_text: bool=False):
        self.name = name
        self.description = description
        self.suggestion = suggestion
        self.expects_original_text = expects_original_text

    def __repr__(self):
        return '[{0}]'.format(self.name)

    def reason(self, violation: RuleViolation=None):
        """ Return a reason for why a given violation occurred.

            Base behavior is to format any associated meta information from the violation into
            the reason/description string as defined by the rule.

            Subclasses may override to provide customized formatting.
        """

        if self.description is not None and violation.meta is not None:
            return self.description.format(**violation.meta)

        return self.description

    def solution(self, violation: RuleViolation=None):
        """ Return a solution for fixing a given violation.

            Base behavior is to format any associated meta information from the violation into
            the solution/suggestion string as defined by the rule.

            Subclasses may override to provide customized formatting.
        """

        if self.suggestion is not None and violation.meta is not None:
            return self.suggestion.format(**violation.meta)

        return self.suggestion

    def augment(self, violation: RuleViolation):
        """ Augment a violation to improve hints of its occurrence.

            Subclasses may override and provide custom augments.
        """

        pass

    def violate(self, at: (int, int), lines: List[Tuple[int, str]]=list(), meta: dict=None) -> RuleViolation:
        """ Return a rule violation originating from a chunk of text. """

        return RuleViolation(self, at, lines, meta)

    def collect(self, text: str, filename: str, extension: str) -> List[RuleViolation]:
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

