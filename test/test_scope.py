# coding=utf-8

import sys

sys.path.append("..")

from comply.util.scope import depth


def test_scope_depth():
    text = 'scope [0] { [1] { [2] } [3] } { [4]'

    assert depth(text.index('[0]'), text) == 0
    assert depth(text.index('[1]'), text) == 1
    assert depth(text.index('[2]'), text) == 2
    assert depth(text.index('[3]'), text) == 1
    assert depth(text.index('[4]'), text) == 1
