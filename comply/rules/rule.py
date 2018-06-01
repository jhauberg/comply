# coding=utf-8

"""
Models for defining rules and violations.
"""

import datetime
import comply

from typing import List, Tuple

from comply.rules.report import CheckFile

from comply.printing import Colors


class RuleViolation:
    """ Represents an occurence of a rule violation. """

    """ A hint to indicate that a violation typically only occur once per file. """
    ONCE_PER_FILE = 1

    """ A hint to indicate that a violation may occur more than once per file. """
    MANY_PER_FILE = 0

    """ A severity indicator for violations that have a negative impact, 
        but can't be objectively deemed an issue.
        
        These violations typically represent code smells or refactoring opportunities.
    """
    ALLOW = 0

    """ A severity indicator for violations that have an objectively negative impact.
    
        These violations should be considered warnings.
        
        This is the default severity.
    """
    WARN = 1

    """ A severity indicator for violations that have an objectively severe negative impact.
    
        These violations should be considered errors.
    """
    DENY = 2

    def __init__(self, which: 'Rule', starting: (int, int), ending: (int, int), lines: List[Tuple[int, str]], meta: dict=None):
        self.which = which
        self.starting = starting
        self.ending = ending
        self.lines = lines
        self.meta = meta

    def __repr__(self):
        return '{0} at {1}'.format(self.which, self.lines)

    def index_of_starting_line(self) -> int:
        """ Return the index of the line where this violation occurs.

            Note that the index *is not* the same as the line number.
        """

        violating_line_number = self.starting[0]

        return self.index_of_line_number(violating_line_number)

    def index_of_line_number(self, line_number: int) -> int:
        """ Return the index of the line that corresponds to a line number.

            Note that the index *is not* the same as the line number.
        """

        line_numbers = [line[0] for line in self.lines]

        violating_line_index = line_numbers.index(line_number)

        return violating_line_index

    @staticmethod
    def report_severity_as(severity: int, is_strict: bool) -> int:
        """ Return an elevated severity indicator for some severities when strict compliance
            is enabled.

            ALLOW becomes WARN
            WARN  remains WARN
            DENY  remains DENY
        """

        should_increase_severity = severity < RuleViolation.WARN and is_strict

        return severity + (1 if should_increase_severity else 0)


class Rule:
    """ Represents a single rule. """

    def __init__(self, name: str, description: str, suggestion: str=None):
        self.name = name
        self.description = description
        self.suggestion = suggestion

        if comply.PROFILING_IS_ENABLED:
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
        """ Augment the offending lines of a violation to improve hints of its occurrence.

            Default implementation applies coloring spanning the range of the occurence.

            Subclasses may override to provide customized augments.
        """

        if len(violation.lines) == 0:
            # nothing to augment; this violation has not captured any lines
            return

        starting_line_number, starting_column = violation.starting
        ending_line_number, ending_column = violation.ending

        starting_line_index = violation.index_of_line_number(starting_line_number)
        ending_line_index = violation.index_of_line_number(ending_line_number)

        starting_char_index = starting_column - 1
        ending_char_index = ending_column - 1

        # go through each affected line, with the ending line included
        for line_index in range(starting_line_index, ending_line_index + 1):
            line_number, line = violation.lines[line_index]

            if line_index == starting_line_index:
                # markup begins on this line
                if starting_line_index == ending_line_index:
                    # markup also ends on this line
                    line = (line[:starting_char_index] + Colors.BAD +
                            line[starting_char_index:ending_char_index] + Colors.RESET +
                            line[ending_char_index:])
                else:
                    # markup exceeds this line
                    line = (line[:starting_char_index] + Colors.BAD +
                            line[starting_char_index:] + Colors.RESET)
            elif line_index == ending_line_index:
                # markup ends on this line
                line = (Colors.BAD + line[:ending_char_index] +
                        Colors.RESET + line[ending_char_index:])
            else:
                # markup spans entire line
                line = (Colors.BAD + line +
                        Colors.RESET)

            violation.lines[line_index] = (line_number, line)

    def violate(self, at: (int, int), to: (int, int)=None, lines: List[Tuple[int, str]]=list(), meta: dict=None) -> RuleViolation:
        """ Return a rule violation spanning over a range of consecutive line numbers and
            columns.

            Captured lines do not have to match with the provided ranges.
        """

        if to is None:
            to = at

        return RuleViolation(self, at, to, lines, meta)

    def violate_at_file(self, file: CheckFile) -> RuleViolation:
        """ Return a violation spanning no lines or characters, starting from the beginning of a
            file.
        """

        return self.violate(at=file.line_number_at_top())

    def violate_at_match(self, file: CheckFile, at) -> RuleViolation:
        """ Return a rule violation spanning the full result of a match. """

        return self.violate_at_character_range(file, starting=at.start(), ending=at.end())

    def violate_at_character_range(self, file: CheckFile, starting: int, ending: int=-1) -> RuleViolation:
        """ Return a rule violation spanning over a range of character indices. """

        if ending < 0:
            ending = starting

        starting_line_number, starting_column = file.line_number_at(starting)
        ending_line_number, ending_column = file.line_number_at(ending)

        offending_lines = file.lines_in_character_range((starting, ending))

        return self.violate(at=(starting_line_number, starting_column),
                            to=(ending_line_number, ending_column),
                            lines=offending_lines)

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
        """ Mark the beginning of a violation collection. """

        self.time_started_collecting = datetime.datetime.now()

    def profile_end(self):
        """ Mark the end of a violation collection and accumulate the time taken. """

        time_since_started_collecting = datetime.datetime.now() - self.time_started_collecting
        time_spent_collecting = time_since_started_collecting / datetime.timedelta(seconds=1)

        self.total_time_spent_collecting += time_spent_collecting

        self.time_started_collecting = None

    @staticmethod
    def rules_in(modules: list) -> list:
        """ Return a list of instances of all Rule-subclasses found in the provided modules.

            Does not recurse through submodules.
        """

        classes = []

        def is_rule_implementation(cls):
            """ Determine whether a class is a Rule implementation. """

            return cls != Rule and type(cls) == type and issubclass(cls, Rule)

        for module in modules:
            for item in dir(module):
                attr = getattr(module, item)

                if is_rule_implementation(attr):
                    classes.append(attr)

        instances = [c() for c in classes]

        return instances
