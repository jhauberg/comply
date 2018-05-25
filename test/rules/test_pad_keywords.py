# coding=utf-8

from comply.rules.standard import PadKeywords

from test.rules.expect import match_triggers


def test_pad_keywords():
    texts = [
        # triggers
        '↓if() { ... }',
        '↓for() { ... }',
        '↓while() { ... }',
        '↓switch() { ... }',
        'if () { ... }↓else{ }',  # only 1 non-overlapping match
        'if (a == b) { ... }↓else if (a == c) { ... } ↓else{ ... }',
        # non-triggers
        'my_format = "switcheroo";',
        'myformat = forx',
        'myif();',
        'myfunc(iflags);',
        '#ifndef'
    ]

    match_triggers(texts, PadKeywords)
