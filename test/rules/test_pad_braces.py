# coding=utf-8

from comply.rules.standard import PadBraces

from test.rules.expect import match_triggers


def test_pad_braces():
    texts = [
        # triggers
        '↓{a, b, c }',
        '↓{a, b, c↓}',
        'if ((struct a_t)↓{ .x = 0↓})↓{ ... ↓}else ↓{something }',
        # non-triggers
        '{ a, b, c }',
        ('{\n'
         'a\n'
         '}')
    ]

    match_triggers(texts, PadBraces)
