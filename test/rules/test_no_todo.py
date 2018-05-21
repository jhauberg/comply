# coding=utf-8

from comply.rules.standard import NoTodo
from comply.checking import check_text


RULE = NoTodo()


def test_no_todo_triggers():
    triggers = ['source with a // todo: find me',
                'source with a // TODO: find me',
                'source           todo: f']

    for text in triggers:
        result = check_text(text, [RULE])

        assert len(result.violations) == 1
        assert result.violations[0].where == (1, 18)

def test_no_todo_non_triggers():
    triggers = ['source with a // todo don\'t find me',
                'source with a // TODO don\'t find me',
                'source todo']

    for text in triggers:
        result = check_text(text, [RULE])

        assert len(result.violations) == 0
