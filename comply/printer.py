# coding=utf-8

from collections import OrderedDict

from comply.util import truncated, Ellipsize


def without_duplicates(pairs: OrderedDict) -> dict:
    unique_pairs = {}

    for key, value in reversed(pairs.items()):
        if value not in unique_pairs.values():
            unique_pairs[key] = value

    return unique_pairs


def print_offenders(offenders: list, filepath: str, with_solutions: bool=True):
    occurences = []
    solutions = OrderedDict() if with_solutions else None

    for offender in offenders:
        location = '{0}:{1}'.format(
            truncated(filepath, length=28, ellipsize=Ellipsize.middle),
            offender.where)

        reason = '[{0}] {1}'.format(offender.which.name, offender.which.reason(offender))
        occurence = '{0} {1}'.format(location, offender.what)

        occurences.append((occurence, reason))

        if with_solutions:
            solutions[occurence] = offender.which.solution(offender)

    if with_solutions:
        solutions = without_duplicates(solutions)

    for occurence, reason in occurences:
        print('{0} -> {1}'.format(occurence, reason))

        if with_solutions and occurence in solutions:
            print(solutions[occurence])
