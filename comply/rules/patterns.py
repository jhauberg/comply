# coding=utf-8

"""
Commonly used patterns for matching C-like syntax.
"""

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

INCLUDE_PATTERN = (r'#include\s*'        # starting with #include and zero or more whitespace
                   r'[<"]'               # up to a starting angle bracket or quote
                   r'(?P<filename>.+?)'  # anything between, but at least one character
                   r'[>"]')              # until ending with angle bracket or quote


COMMENT_BLOCK_PATTERN = r'/\*(?:.|[\n])*?\*/'
# note that this pattern requires re.MULTILINE
COMMENT_LINE_PATTERN = (r'(?:[^:]|^)'  # avoid matching URLs in code, but anything else goes
                        r'//'          # starting point of a single-line comment
                        r'.*?'         # anything following
                        r'(?:\n|$)')   # until reaching end of string or a newline

# match single-line string literals, allowing escaped (\") quotes inside
# note: this does *not* match multi-line literals
LITERAL_SINGLE_LINE = r'(?<!\'|\\)\"([^\"\\\n]*(?:\\.[^\"\\\n]*)*)\"(?!\')'
LITERAL_SINGLE_CHAR = (r'(?<!\'|\\)'  # not preceded by single quote or escape char
                       r'\''          # starting with single quote
                       r'(.{0,2})'    # any single character (up to 2, to allow escape chars)
                       r'\''          # ending with single quote
                       r'(?!\')')     # but not followed by single quote

KEYWORDS = (r'else if|'     # note that this should be matched before the singular if/else
            r'(?<!#)if|'    # exclude pre-processor #if directives
            r'(?<!#)else|'  # exclude pre-processor #else directives
            r'for|'         #
            r'while|'       #
            r'switch')      #
