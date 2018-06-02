# coding=utf-8

from comply.rules.standard import SplitByName

from test.rules.expect import match_triggers


def test_split_by_name():
    texts = [
        # triggers
        'void ↓func(void) { ... }',
        # non-triggers
        'void func();',
        ('void\n'
         'func(void) { ... }'),
        # false-positives
        ('#define ↓YouMessage(pointer, prefix, text) \\\n'
         '    strcat((YouPrefix(pointer, prefix, text), pointer), text)\n'
         '\n'
         'void You\n'
         'VA_DECL(const char *, line)\n'
         '{'),
        ('#if ↓defined(SUPPORT_DEFAULT_FONT)\n'
         'extern void LoadDefaultFont(void)\n'
         '{')
    ]

    match_triggers(texts, SplitByName)
