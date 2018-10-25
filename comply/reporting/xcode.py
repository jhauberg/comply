# coding=utf-8

"""
Provides an implementation of a reporting mode for Xcode.
"""

from comply.rules.rule import Rule

from comply.reporting.oneline import OneLineReporter


class XcodeReporter(OneLineReporter):
    """ Provides reporting output formatted using one line per violation, specifically for Xcode
        to display warning/error boxes.
    """

    def format_message(self, reason: str, rule: Rule) -> str:
        return '{0}'.format(reason)
