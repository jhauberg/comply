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

        for reason, violations in grouped.items():
            results = []

            for violation in violations:
                rule = violation.which

                rule.augment(violation)

                location = Colors.vague + '{0}:'.format(truncated_path) + Colors.clear

                why = '{w}{0} {vague}[{1}]'.format(reason, rule.name,
                                                   w=Colors.warn,
                                                   vague=Colors.vague)
                why = why + Colors.clear

                solution = rule.solution(violation)

                if len(violation.lines) > 0:
                    context = ''

                    for i, (linenumber, line) in enumerate(violation.lines):
                        if linenumber is None:
                            linenumber = ''

                        line = line.expandtabs(4)

                        context += Colors.emphasis + str(linenumber) + Colors.clear
                        context += Colors.clear + '\t{0}'.format(line)

                        if i != len(violation.lines) - 1:
                            context += '\n'

                    output = '{1} {0}\n{2}\n{strong}{3}'.format(why, location, context, solution,
                                                                strong=Colors.strong)
                else:
                    output = '{1} {0}\n{strong}{2}'.format(why, location, solution,
                                                           strong=Colors.strong)

                results.append('\n' + output + Colors.clear)

            self.report_results(results, prefix_if_suppressed='\n')

        printout('')
