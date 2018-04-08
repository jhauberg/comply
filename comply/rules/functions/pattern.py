# coding=utf-8

# match all functions; prototypes, implementations and calls
FUNC_PATTERN = r'(?P<name>\b\w*)\((?P<params>[^!@#$+%^{};]*)\)'

# match only prototypes
FUNC_PROT_PATTERN = FUNC_PATTERN + r'(?=\s*;)'
# match only implementations
FUNC_IMPL_PATTERN = FUNC_PATTERN + r'(?=\s*{)'
# match both
FUNC_BOTH_PATTERN = FUNC_PATTERN + r'(?=\s*(?:;|{))'

# match function bodies (except collapsed bodies, e.g.: '{}')
# note: this pattern will match the inner-most bodies
FUNC_BODY_PATTERN = r'{([^{}]+)}'
