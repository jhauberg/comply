# coding=utf-8

import comply.rules

from comply.rules.rule import Rule

from test.expect import match_triggers

rulesets = [comply.rules.standard]

rules = Rule.rules_in(rulesets)


def test_rule_triggers():
    for rule in rules:
        texts = rule.triggers + rule.nontriggers

        match_triggers(texts, rule, assumed_filename=rule.triggering_filename)


def test_no_duplicates():
    seen_names = set()

    for rule in rules:
        name = rule.name

        assert name not in seen_names

        seen_names.add(name)
