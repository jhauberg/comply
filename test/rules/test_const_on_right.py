# coding=utf-8

import sys

sys.path.append("..")

from comply.rules.misc import ConstOnRight
from comply.checking import check_text


RULE = ConstOnRight()


def test_const_on_right_1():
    texts = ['const int a = 1;',
             'const int * const b = &a;',
             'const struct mytype_t * const c = NULL;']

    for text in texts:
        result, _ = check_text(text, [RULE])

        assert len(result.violations) == 1

        line_number, column = result.violations[0].where

        assert line_number == 1 and column == 1


def test_const_on_right_4():
    text = ('const int32_t\n'
            'card__compare_by_suit(const struct card * const lhs,\n'
            '                      const struct card * const rhs)')

    result, _ = check_text(text, [RULE])

    assert len(result.violations) == 3

    line_number, column = result.violations[0].where

    assert line_number == 1 and column == 1

    line_number, column = result.violations[1].where

    assert line_number == 2 and column == 23

    line_number, column = result.violations[2].where

    assert line_number == 3 and column == 23
