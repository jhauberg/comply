# coding=utf-8

import sys

sys.path.append("..")

from comply.util.truncation import truncated, Ellipsize


def test_text_truncated_at_end():
    text = 'a truncated piece of text'

    truncated_text = truncated(text, length=10, options=Ellipsize.options(Ellipsize.end))

    assert truncated_text == 'a trunc...'


def test_text_truncated_at_start():
    text = 'a truncated piece of text'

    truncated_text = truncated(text, length=10, options=Ellipsize.options(Ellipsize.start))

    assert truncated_text == '...of text'


def test_text_truncated_at_middle():
    text = 'a truncated piece of text'

    truncated_text = truncated(text, length=10, options=Ellipsize.options(Ellipsize.middle))

    assert truncated_text == 'a tr...ext'

