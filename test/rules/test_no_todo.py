# coding=utf-8

from comply.rules.standard import NoTodo

from test.rules.expect import match_triggers


def test_no_todo():
    texts = [
        # triggers
        'source with a // ↓todo: find me',
        'source with a // ↓TODO: find me',
        'source           ↓todo: f',
        # non-triggers
        'source with a // todo don\'t find me',
        'source with a // TODO don\'t find me',
        'source todo'
    ]

    match_triggers(texts, NoTodo)
