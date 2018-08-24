# coding=utf-8

from comply.rules.standard import NoDuplicateIncludes

from test.rules.expect import match_triggers


def test_no_dupe_includes():
    texts = [
        # triggers
        ('#include <header.h>\n'
         '↓#include <header.h>'),
        ('#include "header.h"\n'
         '↓#include "header.h"'),
        ('#include <header.h>\n'
         '↓#include "header.h"'),
        ('#include "header.h"\n'
         '↓#include <header.h>'),
        # non-triggers
        ('#include <header.h>\n'
         '#include <other_header.h>\n'
         '#include "and_another_header.h"\n')
    ]

    match_triggers(texts, NoDuplicateIncludes)
