# coding=utf-8

"""
Provides an implementation of a reporting mode for machines or editors.
"""

import os

from comply.rules.rule import Rule, RuleViolation

from comply.reporting.base import Reporter


class OneLineReporter(Reporter):
    """ Provides reporting output formatted using one line per violation,
        in a Clang, or GCC-like fashion.

        Useful for lean reports or integration with editors.
    """

    def report_before_checking(self, path: str, encoding: str=None, show_progress: bool=True):
        # disable showing progress
        super(OneLineReporter, self).report_before_checking(path, encoding, show_progress=False)

    def format_message(self, reason: str, rule: Rule) -> str:
        return '{0} [{1}]'.format(reason, rule.name)

    def report(self, violations: list, path: str):
        """ Looks like:

            /nethack/src/vision.c:1:81: warning: Line is too long (118 > 80) [line-too-long]
        """

        absolute_path = os.path.abspath(path)

        # group violations by reason so that we can suppress similar ones
        grouped = self.group_by_reason(violations)

        for reason, violations in grouped.items():
            results = []

            for violation in violations:
                line_number, column = violation.starting

                if column > 0:
                    location = '{0}:{1}:{2}:'.format(absolute_path, line_number, column)
                else:
                    location = '{0}:{1}:'.format(absolute_path, line_number)

                rule = violation.which

                severity = RuleViolation.report_severity_as(rule.severity, self.is_strict)

                kind = ('error' if severity > RuleViolation.WARN else
                        ('warning' if severity > RuleViolation.ALLOW else
                         'note'))

                message = self.format_message(reason, rule)
                output = '{0} {1}: {2}'.format(location, kind, message)

                results.append(output)

            self.report_results(results)
