# coding=utf-8

from comply.rules.standard import NoRedundantSize

from test.rules.expect import match_triggers


def test_no_padded_parens():
    texts = [
        # triggers
        'void func(int arr[↓12]);',
        'void func(int a, int arr[  ↓12  ]);',
        'void func(int arr[↓12]) { ... }',
        # non-triggers
        'void func(int (* arr)[12]);',
    ]

    match_triggers(texts, NoRedundantSize)
