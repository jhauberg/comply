# coding=utf-8

from comply.rules.standard import TooManyBlanks

from test.rules.expect import match_triggers


def test_too_many_blanks():
    texts = [
        # triggers
        ('source with some blank lines\n'
         '\n'
         '\n'
         '↓more source'),
        # non-triggers
        ('source with a single blank line\n'
         '\n'
         'more source')
    ]

    match_triggers(texts, TooManyBlanks)
