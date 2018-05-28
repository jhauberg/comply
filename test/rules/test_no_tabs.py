# coding=utf-8

from comply.rules.standard import NoTabs

from test.rules.expect import match_triggers


def test_no_tabs_triggers():
    texts = [
        # triggers
        'source with a↓	tab'
        # non-triggers
        'source without tabs'
    ]

    match_triggers(texts, NoTabs)
