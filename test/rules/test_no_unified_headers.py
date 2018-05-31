# coding=utf-8

from comply.rules.standard import NoUnifiedHeaders

from test.rules.expect import match_triggers


def test_no_unified_headers():
    texts = [
        # triggers
        ('▶// some header file\n'
         '#include <header.h>\n'
         '#include "other_header.h"'),
        # non-triggers
        ('// some header file\n'
         '#include <header.h>\n'
         '#include "other_header.h"'
         'void proto_func(int a);')
    ]

    match_triggers(texts, NoUnifiedHeaders, assumed_filename='header.h')
