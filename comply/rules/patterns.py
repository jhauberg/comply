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

INCLUDE_PATTERN = r'#include\s+[<"].+?[>"]'

COMMENT_BLOCK_PATTERN = r'/\*(?:.|[\n])*?\*/'
COMMENT_LINE_PATTERN = r'[^:]//[\s\S]*?(?:\n|$)'

# match single-line string literals, allowing escaped (\") quotes inside
# note: this does *not* match multi-line literals
LITERAL_SINGLE_LINE = r'(?<!\'|\\)\"([^\"\\\n]*(?:\\.[^\"\\\n]*)*)\"(?!\')'
