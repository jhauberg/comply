# coding=utf-8

from comply.rules.standard import NoPaddedParens

from test.rules.expect import match_triggers


def test_no_padded_parens():
    texts = [
        # triggers
        'func(↓ a, b, c)',
        'func(a, b, c↓ )',
        'func(↓  a, b, c↓ )',
        # non-triggers
        'func(a, b, c)',
    ]

    match_triggers(texts, NoPaddedParens)
