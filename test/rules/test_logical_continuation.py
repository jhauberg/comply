# coding=utf-8

from comply.rules.standard import LogicalContinuation

from test.rules.expect import match_triggers


def test_line_too_long():
    texts = [
        # triggers
        ('if (flag_a\n'
         ' ↓&& flag_b)'),
        ('if (flag_a\n'
         ' ↓|| flag_b)'),
        # non-triggers
        ('if (flag_a &&\n'
         '    flag_b)'),
        ('if (flag_a ||\n'
         '    flag_b)'),
    ]

    match_triggers(texts, LogicalContinuation)
