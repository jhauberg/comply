# coding=utf-8

from comply.rules.standard import PadCommas

from test.rules.expect import match_triggers


def test_pad_commas():
    texts = [
        # triggers
        'func(int a↓,int b)',
        '#define MACRO(a↓,b↓,c)',
        # non-triggers
        'func(int a, int b)',
        ('void func(int a,\n'
         '          int b')
    ]

    match_triggers(texts, PadCommas)
