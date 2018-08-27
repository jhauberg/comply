# coding=utf-8

from comply.rules.standard import FileTooLong

from test.rules.expect import match_triggers


def test_file_too_long():
    texts = []

    def make_filebody(length: int) -> str:
        body = ''

        for i in range(0, length):
            body += '{n}/{c}: line\n'.format(n=i, c=length)

        return body

    # triggers
    texts.append('▶' + make_filebody(FileTooLong.MAX + 1))
    # non-triggers
    texts.append(make_filebody(FileTooLong.MAX))
    texts.append(make_filebody(FileTooLong.MAX - 1))

    match_triggers(texts, FileTooLong)
