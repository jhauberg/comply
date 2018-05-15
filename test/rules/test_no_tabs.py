# coding=utf-8

from comply.rules.standard import NoTabs
from comply.checking import check_text


RULE = NoTabs()


def test_no_tabs_triggers():
    text = 'source with a	tab'
    result = check_text(text, [RULE])

    assert result.num_severe_violations == 1
    assert len(result.violations) == 1
    assert result.violations[0].where == (1, 14)
