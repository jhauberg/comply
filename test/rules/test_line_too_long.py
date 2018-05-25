# coding=utf-8

from comply.rules.standard import LineTooLong

from test.rules.expect import match_triggers


def test_line_too_long():
    texts = [
        # triggers
        'this line is waaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaay ↓too long',
        'this line is waaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaay too lon↓g',
        # non-triggers
        'this line is nooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooot',
        'neither is this liiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiine'
    ]

    match_triggers(texts, LineTooLong)
