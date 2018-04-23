Test sources for the `comply` package.

## Requirements

The tests are simple scripts that could be run as-is, as such, there are no hard requirements. However, using `pytest` is highly recommended as it provides automatic test discovery.

See https://docs.pytest.org/en/latest on how to install and use.

### Running tests

Assuming `pytest` is used as test runner, you just go to the `test` directory and run `pytest`, e.g.:

*Note that it is important that working directory is the `test` directory- otherwise imports from the test scripts won't resolve*

```
$ pytest
```
