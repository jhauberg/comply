# coding=utf-8

from comply.rules.standard import FunctionTooLong

from test.rules.expect import match_triggers


def test_function_too_long():
    texts = []

    def make_funcbody(length: int, expects_violation: bool=False) -> str:
        body = 'void ↓func() {' if expects_violation else 'void func() {'

        for i in range(0, length):
            body += '{n}/{c}: line\n'.format(n=i, c=length)

        body += '}'

        return body

    # triggers
    texts.append(make_funcbody(FunctionTooLong.MAX + 1, expects_violation=True))
    # non-triggers
    texts.append(make_funcbody(FunctionTooLong.MAX))
    texts.append(make_funcbody(FunctionTooLong.MAX - 1))

    match_triggers(texts, FunctionTooLong)
