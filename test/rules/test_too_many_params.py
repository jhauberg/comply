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
        'void func(int a, int b, int c, unsigned short d) { ... }',
        # false-positives
        ('#define ↓DOUBLE_ROUND(v0,v1,v2,v3)  \\\n'  # this is both an issue with pre-processing
         '    HALF_ROUND(v0,v1,v2,v3,13,16); \\\n')  # but also with paren balance- e.g. realizing
                                                     # that function sig actually ends first line
    ]

    match_triggers(texts, TooManyParams)
