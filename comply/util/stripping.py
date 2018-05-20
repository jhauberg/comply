# coding=utf-8

import re

from comply.rules.patterns import (
    FUNC_BODY_PATTERN,
    LITERAL_SINGLE_LINE,
    COMMENT_BLOCK_PATTERN, COMMENT_LINE_PATTERN
)

from comply.util.scope import depth


def is_seemingly_identical(stripped: str, original: str) -> bool:
    """ Determine whether a stripped text has the same line count and
        number of characters as the original text.
    """

    return (len(stripped) == len(original)
            and stripped.count('\n') == original.count('\n'))


def strip_comments(text: str, patterns: list) -> str:
    """ Remove any comments matching provided patterns from a text.

        Entire comment is replaced by whitespace, leaving linebreaks in place.
    """

    stripped = text

    for pattern, flags in patterns:
        flags = 0 if flags is None else flags

        comment_match = re.search(pattern, stripped, flags)

        while comment_match is not None:
            comment = comment_match.group(0)

            replacement = blanked(comment)

            from_index = comment_match.start()
            to_index = comment_match.end()

            stripped = stripped[:from_index] + replacement + stripped[to_index:]

            comment_match = re.search(pattern, stripped, flags)

    assert is_seemingly_identical(stripped, original=text)

    return stripped


def strip_any_comments(text: str) -> str:
    """ Remove both line- and block-style comments from a text. """

    return strip_comments(text, [(COMMENT_BLOCK_PATTERN, None),
                                 (COMMENT_LINE_PATTERN, re.MULTILINE)])


def strip_line_comments(text: str) -> str:
    """ Remove any line-style comments from a text. """

    return strip_comments(text, [(COMMENT_LINE_PATTERN, re.MULTILINE)])


def strip_block_comments(text: str) -> str:
    """ Remove any block-style comments from a text. """

    return strip_comments(text, [(COMMENT_BLOCK_PATTERN, None)])


def strip_function_bodies(text: str) -> str:
    """ Strip and collapse function bodies from a text.

        Entire body is replaced by whitespace, only leaving linebreaks in place.

        Additonally some special rules are applied:

          Inner bodies are stripped including braces
          Outer bodies are stripped leaving collapsed braces behind ({})

        These rules are required to keep the pattern matching from continuing indefinitely,
        while also keeping function patterns matchable against function implementations.
    """

    stripped = text

    body_match = re.search(FUNC_BODY_PATTERN, stripped)

    while body_match is not None:
        leave_braces_behind = False

        if depth(body_match.start(1), stripped) == 1:
            # we hit the outermost function body; strip body including braces,
            # but, at this point we would prefer leaving the braces as-is; however,
            # that would also mean that the pattern would continue matching indefinitely
            # so instead, we leave collapsed braces behind, signifiying an implementation
            # (this can be considered a hack, and some rules may need to be aware of it!)
            leave_braces_behind = True
        else:
            # we hit an inner function body; strip body including braces
            pass

        body = body_match.group()

        replacement = blanked(body)

        if leave_braces_behind:
            # leave behind a collapsed function body
            replacement = '{}' + replacement[1:-1]

        from_index = body_match.start()
        to_index = body_match.end()

        stripped = stripped[:from_index] + replacement + stripped[to_index:]

        body_match = re.search(FUNC_BODY_PATTERN, stripped)

    assert is_seemingly_identical(stripped, original=text)

    return stripped


def strip_literals(text: str) -> str:
    """ Remove any string literals from a text.

        Note that this currently only supports single-line literals.

        Literals inside comments will also be removed.
    """

    return strip_single_line_literals(text)


def strip_single_line_literals(text: str) -> str:
    """ Remove any single-line string literals from a text.

        Stripped characters are replaced with whitespace; literal quote-markers are left behind.

        For example:

          "A bunch of text", if found, becomes:
          "               "

        Note that character literals are not stripped.
    """

    stripped = text

    for match in re.finditer(LITERAL_SINGLE_LINE, stripped):
        literal = match.group(1)

        replacement = ' ' * len(literal)

        from_index = match.start(1)
        to_index = match.end(1)

        # note that we're doing an iterative search *while* we're modifying the text we're
        # matching on; this works out because the number of characters always remain the same
        # (i.e. we're just replacing with whitespace)
        stripped = stripped[:from_index] + replacement + stripped[to_index:]

    assert is_seemingly_identical(stripped, original=text)

    return stripped


def strip_parens(text: str) -> str:
    """ Remove any parentheses blocks. """

    stripped = text

    # note that we search for paren blocks but only use the matches to find a starting position
    # since parens can be nested inside other parens, we have to manually count opening and
    # closing parens to find the entire block that we want to strip
    pattern = re.compile(r'\(.*?\)', re.DOTALL)  # paren blocks can span more than one line

    match = pattern.search(stripped)

    while match is not None:
        starting = match.start()
        ending = starting

        depth_count = 0

        for c in text[starting:]:
            if c == '(':
                depth_count += 1
            elif c == ')':
                depth_count -= 1

            ending += 1

            if depth_count == 0:
                break

        block = text[starting:ending]
        replacement = blanked(block)

        stripped = stripped[:starting] + replacement + stripped[ending:]

        match = pattern.search(stripped)

    return stripped


def blanked(text: str, keepends: bool=True) -> str:
    """ Return text with every character replaced by whitespace.

        Newlines are kept as-is.
    """

    if keepends:
        blanked_text = re.sub(r'[^\s\r\n]', ' ', text)
    else:
        blanked_text = ' ' * len(text)

    return blanked_text
