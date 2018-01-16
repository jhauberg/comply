# coding=utf-8

from collections import OrderedDict


def without_duplicates(suggestions: OrderedDict) -> dict:
    unique_suggestions = {}

    for key, value in reversed(suggestions.items()):
        if value not in unique_suggestions.values():
            unique_suggestions[key] = value

    return unique_suggestions


def print_offenders(offenders: list, with_solutions: bool=True):
    offenses = []
    solutions = OrderedDict() if with_solutions else None

    for offender in offenders:
        offense = str(offender)
        offenses.append(offense)

        if with_solutions:
            solutions[offense] = offender.solution()

    if with_solutions:
        solutions = without_duplicates(solutions)

    for offense in offenses:
        print(offense)

        if with_solutions and offense in solutions:
            print(solutions[offense])
