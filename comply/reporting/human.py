# coding=utf-8

"""
Provides an implementation of a reporting mode for human readers.
"""

import os

from comply.rules.rule import RuleViolation

from comply.reporting.base import Reporter

from comply.printing import printout, Colors


class HumanReporter(Reporter):
    """ Provides reporting output (including suggestions) formatted for human readers. """

    def report(self, violations: list, path: str):
        # determine absolute path of file
        absolute_path = os.path.abspath(path)

        # group violations by reason so that we can suppress similar ones
        grouped = self.group_by_reason(violations)

        num_reported_results = 0

        for reason, violations in grouped.items():
            results = []

            for violation in violations:
                result = self.formatted_result(violation, reason, absolute_path)
                results.append(result)

            num_reported_results += self.report_results(results, prefix_if_suppressed='\n')

        if self.is_verbose and num_reported_results > 0:
            # make sure we separate the "Checking..." message with a newline
            # note that this only occur when --verbose is set
            printout('')

    def formatted_result(self, violation: RuleViolation, reason: str, path: str) -> str:
        """ Return a formatted result of a rule violation. """

        rule = violation.which
        rule.augment(violation)

        location = Colors.DARK + '{0}:'.format(path) + Colors.RESET

        severity = RuleViolation.report_severity_as(rule.severity, self.is_strict)

        severity_color = (Colors.DENY if severity > RuleViolation.WARN else
                          (Colors.WARN if severity > RuleViolation.ALLOW else
                           Colors.ALLOW))

        if reason is None or len(reason) == 0:
            reason = ('Severe violation' if severity > RuleViolation.WARN else
                      ('Cautioned violation' if severity > RuleViolation.ALLOW else
                       'Allowed violation'))

        why = '{tint}{0} {vague}[{1}]'.format(reason, rule.name,
                                              tint=severity_color,
                                              vague=Colors.VAGUE) + Colors.RESET

        solution = rule.solution(violation)

        output = '{reason} in\n{location}'.format(
            reason=why, location=location)

        if len(violation.lines) > 0:
            context = '\n'

            for i, (linenumber, line) in enumerate(violation.lines):
                # a "line" can, in some cases, actually span several lines
                # (typically rules that match functions with parameters spanning several lines,
                # so the entire function signature is considered "the line")
                expanded_lines = HumanReporter.expand_line(linenumber, line)

                for j, (n, l) in enumerate(expanded_lines):
                    if n is None:
                        n = ''

                    line = l.expandtabs(4)

                    context += Colors.EMPHASIS + str(n) + Colors.RESET
                    context += Colors.RESET + '\t{0}'.format(line)

                    if j != len(expanded_lines) - 1:
                        context += '\n'

                if i != len(violation.lines) - 1:
                    context += '\n'

            output += context

        if solution is not None and len(solution) > 0:
            output += '\n{strong}{suggestion}'.format(
                suggestion=solution, strong=Colors.STRONG)

        return '\n' + output + Colors.RESET

    @staticmethod
    def expand_line(line_number: int, line: str):
        """ Like str.splitlines() except including line numbers. """

        if len(line) == 0:
            return [(line_number, line)]

        lines = []

        for i, l in enumerate(line.splitlines()):
            lines.append(
                (line_number + i if line_number is not None else None, l)
            )

        return lines
