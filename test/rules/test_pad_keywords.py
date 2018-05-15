# coding=utf-8

from comply.rules.misc import PadKeywords
from comply.checking import check_text


RULE = PadKeywords()


def test_pad_keywords_1():
    texts = ['if() { ... }',
             'for() { ... }',
             'while() { ... }',
             'switch() { ... }']

    for text in texts:
        result = check_text(text, [RULE])

        assert len(result.violations) == 1

        line_number, column = result.violations[0].where

        assert line_number == 1 and column == 1


def test_pad_keywords_2():
    text = 'if (a == b) { ... }else if (a == c) { ... } else{ ... }'

    result = check_text(text, [RULE])

    assert len(result.violations) == 2

    line_number, column = result.violations[0].where

    assert line_number == 1 and column == 20

    line_number, column = result.violations[1].where

    assert line_number == 1 and column == 45


def test_pad_keywords_3():
    text = 'if () { ... }else{ }'

    result = check_text(text, [RULE])

    assert len(result.violations) == 1

    line_number, column = result.violations[0].where

    assert line_number == 1 and column == 14


def test_pad_keywords_4():
    texts = ['my_format = "switcheroo";',
             'myformat = forx',
             '#ifndef']

    for text in texts:
        result = check_text(text, [RULE])

        assert len(result.violations) == 0
