# coding=utf-8

from comply.rules.standard import SplitByName

from test.rules.expect import match_triggers


def test_split_by_name():
    texts = [
        # triggers
        'void ↓func(void) { ... }',
        # non-triggers
        'void func();',
        ('void\n'
         'func(void) { ... }')
    ]

    match_triggers(texts, SplitByName)
