# coding=utf-8

from comply.rules.standard import PadCommas
from comply.checking import check_text


RULE = PadCommas()


def test_pad_commas_triggers():
    text = 'void func(int a,int b)'

    result = check_text(text, [RULE])

    assert len(result.violations) == 1

    assert result.violations[0].where == (1, 16)


def test_pad_commas_non_triggers():
    text = ('void func(int a,'
            '          int b')

    result = check_text(text, [RULE])

    assert len(result.violations) == 0
