# coding=utf-8

from comply.rules.standard import PadPointerDeclarations

from test.rules.expect import match_triggers


def test_pad_pointer_decls_triggers():
    texts = [
        # triggers
        'char const ↓*a = "abc";',
        '(struct command↓*)cmd',
        'return *((uint64_t↓*)&index);',
        # non-triggers
        'char const * a = "abc";',
        'char const a = *ptr;',
        '*ptr = a;',
        'char const a = b ? c : *ptr;',
        'char const a = b ? *ptr : c;'
    ]

    match_triggers(texts, PadPointerDeclarations)
