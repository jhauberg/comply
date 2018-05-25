# coding=utf-8

from comply.rules.standard import PadPointerDeclarations

from test.rules.expect import match_triggers


def test_pad_pointer_decls_triggers():
    texts = [
        # triggers
        'char const ↓*a = "abc"',
        # non-triggers
        'char const * a = "abc"'
    ]

    match_triggers(texts, PadPointerDeclarations)
