# coding=utf-8

import os

from comply.rules import RuleViolation

from comply.reporting.base import Reporter


class OneLineReporter(Reporter):
    """ Provides reporting output formatted using one line per violation,
        in a Clang, or GCC-like fashion.

        Useful for lean reports or integration with editors.
    """

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
                line, column = violation.where

                if column > 0:
                    location = '{0}:{1}:{2}:'.format(absolute_path, line, column)
                else:
                    location = '{0}:{1}:'.format(absolute_path, line)

                rule = violation.which

                severity = ('error' if rule.severity > RuleViolation.WARN else
                            ('warning' if rule.severity > RuleViolation.ALLOW else
                             'note'))

                why = '{0} [{1}]'.format(reason, rule.name)
                output = '{0} {1}: {2}'.format(location, severity, why)

                results.append(output)

            self.report_results(results)
