# coding=utf-8

import datetime

from typing import List, Tuple

from comply import PROFILING_IS_ENABLED
from comply.rules.report import CheckFile


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


class Rule:
    """ Represents a single rule. """

    def __init__(self, name: str, description: str, suggestion: str=None):
        self.name = name
        self.description = description
        self.suggestion = suggestion

        if PROFILING_IS_ENABLED:
            self.time_started_collecting = None
            self.total_time_spent_collecting = 0

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

    def profile_begin(self):
        if not PROFILING_IS_ENABLED:
            return

        self.time_started_collecting = datetime.datetime.now()

    def profile_end(self):
        if not PROFILING_IS_ENABLED:
            return

        time_since_started_collecting = datetime.datetime.now() - self.time_started_collecting
        time_spent_collecting = time_since_started_collecting / datetime.timedelta(seconds=1)

        self.total_time_spent_collecting += time_spent_collecting

        self.time_started_collecting = None
