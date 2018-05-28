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


TRIGGER_CHAR = '↓'


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
    trigger_indices = []

    for trigger in re.finditer(TRIGGER_CHAR, text):
        # subtract count to determine the correct index when triggers are stripped
        trigger_indices.append(trigger.start() - len(trigger_indices))

    # make a clean snippet without trigger chars
    snippet = text.replace(TRIGGER_CHAR, '')

    # determine locations of all expected violations
    trigger_locations = [CheckFile.line_number_in_text(trigger_index, snippet)
                         for trigger_index in trigger_indices]

    # determine number of expected violations
    expected_number_of_violations = len(trigger_locations)

    if assumed_filename is not None:
        result = check_text(snippet, [rule()], assumed_filename)
    else:
        result = check_text(snippet, [rule()])

    # make sure resulting violations are in ascending order to match the trigger indices
    violations_in_order = sorted(result.violations,
                                 key=lambda v: v.where)

    total_violations = len(violations_in_order)

    if total_violations != expected_number_of_violations:
        violation_locations = [violation.where for violation in violations_in_order]

        raise AssertionError(('Found unexpected number of violations ({0} != {1}):\n'
                              'Found {2}\n'
                              'Expected {3}').format(
            total_violations, expected_number_of_violations, violation_locations, trigger_locations))

    for i, violation in enumerate(violations_in_order):
        trigger_location = trigger_locations[i]

        if violation.where != trigger_location:
            raise AssertionError('Found unexpected violation ({0} != {1})'.format(
                violation.where, trigger_location))
