# coding=utf-8

from comply.rules.standard import ConstOnRight

from test.rules.expect import match_triggers


def test_const_on_right():
    texts = [
        # triggers
        '↓const int a = 1;',
        '↓const int * const b = &a;',
        '↓const struct mytype_t * const c = NULL;',
        'int const a = * (↓const int *)b;',
        ('↓const int32_t\n'
         'my_func(↓const struct mytype_t * const lhs,\n'
         '        ↓const struct mytype_t * const rhs)'),
        # non-triggers
        'int const a = 1;',
        # false-positives
        ('int\n'
         '↓const a = 1;')
    ]

    match_triggers(texts, ConstOnRight)
