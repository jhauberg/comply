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

### Marking and fixing false-positives

Sometimes we find code that produce false-positive violations. This is not unusual given how `comply` works.

When finding these, they should always be captured and noted in a test. This way we have a documented and reproducible case which helps a lot when looking for a fix.

False-positive tests should always be marked under a `# false-positives` section, like so:

```
texts = [
    # triggers
    'void ↓func(int, int, int, unsigned short, long);',
    'void ↓func(int a, int b, int c, unsigned short d, long f);',
    'void ↓func(int a, int b, int c, unsigned short d, long f) { ... }',
    # non-triggers
    'void func(int, int, int, unsigned short);',
    'void func(int a, int b, int c, unsigned short d);',
    'void func(int a, int b, int c, unsigned short d) { ... }',
    # false-positives
    ('#define ↓DOUBLE_ROUND(v0,v1,v2,v3)  \\\n'
     '    HALF_ROUND(v0,v1,v2,v3,13,16); \\\n')
]
```

This way, we can easily [search](https://github.com/search?l=Python&q=false-positives+repo%3Ajhauberg%2Fcomply+path%3A%2Ftest&type=Code) and get a list of all the discovered false-positives.
