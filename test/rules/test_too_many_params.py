# coding=utf-8

from comply.rules.standard import TooManyParams

from test.rules.expect import match_triggers


def test_too_many_params():
    texts = [
        # triggers
        'void ↓func(int, int, int, unsigned short, long);',
        'void ↓func(int a, int b, int c, unsigned short d, long f);',
        'void ↓func(int a, int b, int c, unsigned short d, long f) { ... }',
        # non-triggers
        'void func(int, int, int, unsigned short);',
        'void func(int a, int b, int c, unsigned short d);',
        'void func(int a, int b, int c, unsigned short d) { ... }'
    ]

    match_triggers(texts, TooManyParams)
