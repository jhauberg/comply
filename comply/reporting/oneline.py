# coding=utf-8

import os

from comply.reporting.base import Reporter


class OneLineReporter(Reporter):
    """ Provides violation output formatted in a Clang-like fashion. """

    def report(self, violations: list, path: str):
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

                why = '{0} [{1}]'.format(reason, violation.which.name)
                output = '{0} warning: {1}'.format(location, why)

                results.append(output)

            self.report_similar_results(results)