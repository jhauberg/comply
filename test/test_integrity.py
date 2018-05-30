# coding=utf-8

from comply.rules.rule import Rule

from comply.rules import *


def test_no_rule_duplicates():
    rules = Rule.rules_in([comply.rules.standard,
                           comply.rules.experimental])

    names = set()

    for rule in rules:
        name = rule.name

        assert name not in names

        names.add(name)
