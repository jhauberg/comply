# coding=utf-8

from comply.rules.standard import NoTabs
from comply.checking import check_text


RULE = NoTabs()


def test_no_tabs():
    text = 'source with a	tab'
    result = check_text(text, [RULE])

    assert result.num_severe_violations == 1
    assert len(result.violations) == 1

    line_number, column = result.violations[0].where

    assert line_number == 1 and column == 14
