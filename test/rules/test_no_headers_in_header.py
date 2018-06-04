# coding=utf-8

from comply.rules.standard import NoHeadersInHeader

from test.rules.expect import match_triggers


def test_no_headers_in_header():
    texts = [
        # triggers
        ('// some header file\n'
         '↓#include <header.h>'),
        ('// some header file\n'
         '↓#include <header.h> // type'),
        # non-triggers
        ('#include <stdbool.h>\n'
         '#include <stdint.h>\n'
         '#include <inttypes.h>'),
        ('// some header file\n'
         'struct symbol_t;'),
        '#include <header.h> // type :completeness',
        '#include <header.h> // type:completeness'
    ]

    match_triggers(texts, NoHeadersInHeader, assumed_filename='header.h')
