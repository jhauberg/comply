# coding=utf-8

"""
Helper functions for asserting that the result of a rule check match expectations.

These functions work by looking for 'trigger characters' in a text and determining whether
the locations match with where violations occur.

Example:

    The text 'violate ↓this' expects one violation to occur at 'this'.
    The text 'violate ↓this and ↓that' expects two violations; one at 'this' and one at 'that'
    The text 'violate nothing' expects zero violations

The trigger characters are removed from the text before running the rule check.
"""

import re

from comply.checking import check_text
from comply.rules.report import CheckFile


TRIGGER_AT = '↓'
TRIGGER_LINE = '▶'

pattern = re.compile(r'([{0}{1}])'.format(TRIGGER_LINE, TRIGGER_AT))


def match_triggers(texts: list, rule, assumed_filename: str=None):
    """ Check texts for any violations to a rule and determine whether they match the
        expected results.
    """

    for text in texts:
        check_triggers(text, rule, assumed_filename)


def check_triggers(text: str, rule, assumed_filename: str=None):
    """ Check a text for any violations to a rule and assert whether they
        correspond to the expected count and location.
    """

    # find all expected violation triggers
    triggers = []

    for trigger in pattern.finditer(text):
        trigger_symbol = trigger.group()

        # the offset equals number of triggers added so far- assuming we find them in order
        # (because each trigger before another trigger should be considered as not-there, since
        # they will all be removed from the final text)
        trigger_index_offset = len(triggers)

        triggers.append((trigger_symbol,
                         trigger.start() - trigger_index_offset))

    # make a clean snippet without triggers
    snippet, num_triggers_removed = pattern.subn('', text)

    assert len(triggers) == num_triggers_removed

    # determine locations of all expected violations
    trigger_locations = []

    for trigger_symbol, trigger_index in triggers:
        should_span_entire_line = trigger_symbol == TRIGGER_LINE

        trigger_line_number, trigger_column = CheckFile.line_number_in_text(
            trigger_index, snippet, span_entire_line=should_span_entire_line)

        trigger_locations.append((trigger_line_number, trigger_column))

    # determine number of expected violations
    expected_number_of_violations = len(trigger_locations)

    if assumed_filename is not None:
        result = check_text(snippet, [rule], assumed_filename)
    else:
        result = check_text(snippet, [rule])

    # make sure resulting violations are in ascending order to match the trigger indices
    violations_in_order = sorted(result.violations,
                                 key=lambda v: v.starting)

    total_violations = len(violations_in_order)

    if total_violations != expected_number_of_violations:
        violation_locations = [violation.starting for violation in violations_in_order]

        raise AssertionError(('[{5}] Found unexpected number of violations ({0} != {1}):\n'
                              'Found {2}\n'
                              'Expected {3}\n'
                              'In text:\n{4}').format(
            total_violations, expected_number_of_violations,
            violation_locations, trigger_locations, text, rule.name))

    for i, violation in enumerate(violations_in_order):
        trigger_location = trigger_locations[i]

        if violation.starting != trigger_location:
            raise AssertionError(('[{3}] Found unexpected violation ({0} != {1})\n'
                                  'In text:\n{2}').format(
                violation.starting, trigger_location, text, rule.name))
