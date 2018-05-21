# coding=utf-8

from comply.util.stripping import (
    blanked,
    strip_parens,
    strip_single_line_literals,
    strip_line_comments,
    strip_block_comments
)


def test_blanked():
    text = 'abcd'

    assert blanked(text) == '    '

    text = ('abcd\n'
            'efgh')

    assert blanked(text) == ('    \n'
                             '    ')

    assert blanked(text, keepends=False) == '         '


def test_strip_parens():
    text = 'if (true) {'

    assert strip_parens(text) == 'if        {'

    text = ('if (true)\n'
            '{')

    assert strip_parens(text) == ('if       \n'
                                  '{')

    text = ('if (true &&\n'
            '    true)\n'
            '{')

    assert strip_parens(text) == ('if         \n'
                                  '         \n'
                                  '{')


def test_strip_literals():
    text = 'char const * str = "abc";'

    assert strip_single_line_literals(text) == 'char const * str = "   ";'

    text = 'char a = \'"\'; char b = \'"\''

    assert strip_single_line_literals(text) == text


def test_strip_literal_chars():
    #text = r'test "this" and 't' but not "\' f'" or 'asd' nor  but yes to '\'''
    pass


def test_strip_line_comments():
    text = 'char a; // strip me'

    assert strip_line_comments(text) == 'char a;            '


def test_strip_block_comments():
    text = '/** strip me */'

    assert strip_block_comments(text) == '               '

    text = '/** strip me // fully */'

    assert strip_block_comments(text) == '                        '

    text = ('/**\n'
            ' * strip * me\n'
            ' */\n'
            'char a;')

    assert strip_block_comments(text) == ('   \n'
                                          '             \n'
                                          '   \n'
                                          'char a;')
