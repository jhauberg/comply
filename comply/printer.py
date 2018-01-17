# coding=utf-8

from collections import OrderedDict

from comply.util import truncated, Ellipsize


def without_duplicates(suggestions: OrderedDict) -> dict:
    unique_suggestions = {}

    for key, value in reversed(suggestions.items()):
        if value not in unique_suggestions.values():
            unique_suggestions[key] = value

    return unique_suggestions


def print_offenders(offenders: list, filepath: str, with_solutions: bool=True):
    offenses = []
    solutions = OrderedDict() if with_solutions else None

    for offender in offenders:
        rule = offender.which.representation(offender)

        location = '{0}:{1}'.format(
            truncated(filepath, length=28, ellipsize=Ellipsize.middle), offender.where)

        offense = '{0} -> {1} {2}'.format(rule, location, offender.what)

        offenses.append(offense)

        if with_solutions:
            solutions[offense] = offender.which.solution(offender)

    if with_solutions:
        solutions = without_duplicates(solutions)

    for offense in offenses:
        print(offense)

        if with_solutions and offense in solutions:
            print(solutions[offense])
