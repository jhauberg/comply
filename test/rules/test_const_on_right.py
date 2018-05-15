# coding=utf-8

from comply.rules.standard import ConstOnRight
from comply.checking import check_text


RULE = ConstOnRight()


def test_const_on_right_triggers():
    texts = ['const int a = 1;',
             'const int * const b = &a;',
             'const struct mytype_t * const c = NULL;']

    for text in texts:
        result = check_text(text, [RULE])

        assert len(result.violations) == 1

        assert result.violations[0].where == (1, 1)


def test_const_on_right_2():
    text = 'int const a = * (const int *)b;'

    result = check_text(text, [RULE])

    assert len(result.violations) == 1

    assert result.violations[0].where == (1, 18)


def test_const_on_right_3():
    text = ('const int32_t\n'
            'card__compare_by_suit(const struct card * const lhs,\n'
            '                      const struct card * const rhs)')

    result = check_text(text, [RULE])

    assert len(result.violations) == 3

    assert result.violations[0].where == (1, 1)
    assert result.violations[1].where == (2, 23)
    assert result.violations[2].where == (3, 23)


def test_const_on_right_false_positive():
    # this should not cause a violation, but does; see #45
    # this test asserts that the false-positive is still in effect
    text = ('int\n'
            'const a = 1;')

    result = check_text(text, [RULE])

    assert len(result.violations) == 1
