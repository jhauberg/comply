# coding=utf-8

import sys

sys.path.append("..")

from comply.util.stripping import *


def test_blanked():
    text = 'abcd'

    assert blanked(text) == '    '

    text = ('abcd\n'
            'efgh')

    assert blanked(text) == ('    \n'
                             '    ')


def test_strip_literals():
    text = 'char const * str = "abc";'

    assert strip_literals(text) == 'char const * str = "   ";'

    text = 'char a = \'"\'; char b = \'"\''

    assert strip_literals(text) == text


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
