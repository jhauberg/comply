Test sources for the `comply` package.

## Requirements

The tests are simple scripts that could be run as-is, as such, there are no hard requirements. However, using `pytest` is highly recommended as it provides automatic test discovery.

See https://docs.pytest.org/en/latest on how to install and use.

### Running tests

Assuming `pytest` is used as test runner, you just go to the `test` directory and run `pytest`, e.g.:

```
$ pytest
```

*Note that it is important that working directory is the `test` directory- otherwise imports from the test scripts won't resolve*

### Making tests

As mentioned, tests should be small, simple and concise scripts that `assert` that expectations match results.

The utility script [`expect.py`](rules/expect.py) can be used for conveniently testing whether rules produce violations on the expected lines/columns.

For example, this test checks the `PadPointerDeclarations` rule:

```
texts = [
    # triggers
    'char const ↓*a = "abc"',
    # non-triggers
    'char const * a = "abc"'
]

match_triggers(texts, PadPointerDeclarations)
```

Note the `↓` character, which is used to indicate that a violation occurs at this exact line and column. There can be multiple triggers in a text.

Similarly, the `▶` character can be used to indicate that a violation occurs for an entire line, for example:

```
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
```

*Some rules expect a filename; this can be provided through `assumed_filename`- the file does not have to exist.*