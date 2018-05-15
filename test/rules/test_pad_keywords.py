# coding=utf-8

from comply.rules.standard import PadKeywords
from comply.checking import check_text


RULE = PadKeywords()


def test_pad_keywords_triggers():
    texts = ['if() { ... }',
             'for() { ... }',
             'while() { ... }',
             'switch() { ... }']

    for text in texts:
        result = check_text(text, [RULE])

        assert len(result.violations) == 1
        assert result.violations[0].where == (1, 1)


def test_pad_keywords_non_triggers():
    texts = ['my_format = "switcheroo";',
             'myformat = forx',
             'myif();',
             'myfunc(iflags);',
             '#ifndef']

    for text in texts:
        result = check_text(text, [RULE])

        assert len(result.violations) == 0


def test_pad_keywords_2():
    text = 'if (a == b) { ... }else if (a == c) { ... } else{ ... }'

    result = check_text(text, [RULE])

    assert len(result.violations) == 2

    assert result.violations[0].where == (1, 20)
    assert result.violations[1].where == (1, 45)


def test_pad_keywords_3():
    text = 'if () { ... }else{ }'

    result = check_text(text, [RULE])

    assert len(result.violations) == 1

    assert result.violations[0].where == (1, 14)
