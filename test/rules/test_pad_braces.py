# coding=utf-8

from comply.rules.standard import PadBraces
from comply.checking import check_text


RULE = PadBraces()


def test_pad_braces_triggers():
    text = '{0}'

    result = check_text(text, [RULE])

    assert len(result.violations) == 1  # only 1, because matches otherwise overlap

    assert result.violations[0].where == (1, 1)

    text = '{13}'

    result = check_text(text, [RULE])

    assert len(result.violations) == 2

    assert result.violations[0].where == (1, 1)
    assert result.violations[1].where == (1, 4)

    text = 'if ((struct a_t){ .x = 0}){ ... }else {something }'

    result = check_text(text, [RULE])

    assert len(result.violations) == 5

    assert result.violations[0].where == (1, 17)
    assert result.violations[1].where == (1, 25)
    assert result.violations[2].where == (1, 27)
    assert result.violations[3].where == (1, 33)
    assert result.violations[4].where == (1, 39)
