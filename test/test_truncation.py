# coding=utf-8

import sys

sys.path.append("..")

from comply.util.truncation import truncated, Ellipsize


TEXT = 'a truncated piece of text'
LENGTH = 10


def test_text_truncated_at_end():
    truncated_text = truncated(TEXT,
                               length=LENGTH,
                               options=Ellipsize.options(Ellipsize.end))

    assert truncated_text == 'a trunc...'


def test_text_truncated_at_start():
    truncated_text = truncated(TEXT,
                               length=LENGTH,
                               options=Ellipsize.options(Ellipsize.start))

    assert truncated_text == '...of text'


def test_text_truncated_at_middle():
    truncated_text = truncated(TEXT,
                               length=LENGTH,
                               options=Ellipsize.options(Ellipsize.middle))

    assert truncated_text == 'a tr...ext'


def test_text_truncated_at_ends():
    middle_index = int(len(TEXT) / 2)

    truncated_text = truncated(TEXT,
                               length=LENGTH,
                               options=Ellipsize.options(Ellipsize.ends, index=middle_index))

    assert truncated_text == '...d pi...'
