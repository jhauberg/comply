# coding=utf-8

# base pattern for function prototypes and signatures
FUNC_BASE_PATTERN = r'(?<!return)(?:(?<=[\w*])\s+|\*)(?P<name>\w+)\s*\((?P<params>[^&%^?#@!/<>=+\-{};]*)\)'

# match only prototypes
FUNC_PROT_PATTERN = FUNC_BASE_PATTERN + r'(?=\s*;)'
# match only implementations
FUNC_IMPL_PATTERN = FUNC_BASE_PATTERN + r'(?=\s*{)'
# match both
FUNC_BOTH_PATTERN = FUNC_BASE_PATTERN + r'(?=\s*[{;])'

# match function bodies (except collapsed bodies, e.g.: '{}')
# note: this pattern will match the inner-most bodies
FUNC_BODY_PATTERN = r'{([^{}]+)}'
