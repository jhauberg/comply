# coding=utf-8

import comply.rules

from comply.rules.rule import Rule

from test.expect import match_triggers

rulesets = [comply.rules.standard]

rules = Rule.rules_in(rulesets)


def test_rule_triggers():
    for rule in rules:
        triggers = rule.triggers
        nontriggers = rule.nontriggers

        if len(triggers) == 0:
            raise AssertionError('[{0}] No triggering texts to test'.format(rule.name))

        texts = triggers + nontriggers

        match_triggers(texts, rule, assumed_filename=rule.triggering_filename)


def test_no_duplicates():
    seen_names = set()

    for rule in rules:
        name = rule.name

        assert name not in seen_names

        seen_names.add(name)
