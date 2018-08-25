# coding=utf-8

from comply.rules.standard import NoUnnamedInts

from test.rules.expect import match_triggers


def test_no_unnamed_ints():
    texts = [
        # triggers
        'void func(↓int);',
        'void func(  ↓int);',
        'void func(↓int  );',
        'void func(  ↓int  );',
        ('void func(↓int,\n'
         '          unsigned ↓int);'),
        # non-triggers
        'void func(int a);',
        'void func(int    a);',
        ('void func(int\n'
         '          a);'),
        'void func(struct point);'
    ]

    match_triggers(texts, NoUnnamedInts)
