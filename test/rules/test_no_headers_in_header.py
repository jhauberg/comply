# coding=utf-8

from comply.rules.standard import NoHeadersInHeader

from test.rules.expect import match_triggers


def test_no_headers_in_header():
    texts = [
        # triggers
        ('// some header file\n'
         '↓#include <header.h>'),
        # non-triggers
        ('// some header file\n'
         'struct symbol_t;')
    ]

    match_triggers(texts, NoHeadersInHeader, assumed_filename='header.h')
