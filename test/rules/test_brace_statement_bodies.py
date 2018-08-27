# coding=utf-8

from comply.rules.standard import BraceStatementBodies

from test.rules.expect import match_triggers


def test_brace_statement_bodies():
    texts = [
        # triggers
        '↓if (true) run();',
        ('↓if (true)\n'
         '    run();'),
        # non-triggers
        'if (true) { run(); }',
        ('if (true) {\n'
         '    run();\n'
         '}'),
    ]

    match_triggers(texts, BraceStatementBodies)
