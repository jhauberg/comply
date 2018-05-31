# coding=utf-8

from comply.rules.standard import NoSourceIncludes

from test.rules.expect import match_triggers


def test_no_source_includes():
    texts = [
        # triggers
        '↓#include "source.c"',
        ('// some source file\n'
         '↓#include <source.c>'),
        # non-triggers
        ('// some header file\n'
         '#include <file.h>')
    ]

    match_triggers(texts, NoSourceIncludes)
