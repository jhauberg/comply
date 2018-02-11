# coding=utf-8

import os

from comply.reporting.base import Reporter

from comply.printing import printout, Colors
from comply.util.truncation import truncated, Ellipsize


class HumanReporter(Reporter):
    """ Provides reporting output (including suggestions) formatted for human readers. """

    @property
    def suppress_after(self):
        return 1

    def report(self, violations: list, path: str):
        # determine absolute path of file
        absolute_path = os.path.abspath(path)

        path_length = 24

        # pad if necessary (path too short)
        padded_path = absolute_path.ljust(path_length)
        # truncate if too long
        truncated_path = truncated(padded_path,
                                   length=path_length,
                                   options=Ellipsize.options(at=Ellipsize.start))

        # group violations by reason so that we can suppress similar ones
        grouped = self.group_by_reason(violations)

        number_of_reported_results = 0

        for reason, violations in grouped.items():
            results = []

            for violation in violations:
                rule = violation.which

                rule.augment(violation)

                location = Colors.vague + '{0}:'.format(truncated_path) + Colors.clear

                why = '{w}{0} {vague}[{1}]'.format(reason, rule.name,
                                                   w=Colors.warn,
                                                   vague=Colors.vague) + Colors.clear

                solution = rule.solution(violation)

                if len(violation.lines) > 0:
                    context = ''

                    for i, (linenumber, line) in enumerate(violation.lines):
                        expanded_lines = HumanReporter.expand_lines(linenumber, line)

                        for j, (n, l) in enumerate(expanded_lines):
                            if n is None:
                                n = ''

                            line = l.expandtabs(4)

                            context += Colors.emphasis + str(n) + Colors.clear
                            context += Colors.clear + '\t{0}'.format(line)

                            if j != len(expanded_lines) - 1:
                                context += '\n'

                        if i != len(violation.lines) - 1:
                            context += '\n'

                    output = '{1} {0}\n{2}\n{strong}{3}'.format(why, location, context, solution,
                                                                strong=Colors.strong)
                else:
                    output = '{1} {0}\n{strong}{2}'.format(why, location, solution,
                                                           strong=Colors.strong)

                results.append('\n' + output + Colors.clear)

            number_of_reported_results += self.report_results(results, prefix_if_suppressed='\n')

        if self.is_verbose and number_of_reported_results > 0:
            # make sure we separate the "Checking..." message with a newline
            # note that this only occur when --verbose is set
            printout('')

    @staticmethod
    def expand_lines(line_number: int, line: str):
        """ Like str.splitlines(), except including line numbers. """
        lines = []

        for i, l in enumerate(line.splitlines()):
            current_line_number = line_number + i if line_number is not None else None
            lines.append((current_line_number, l))

        return lines
