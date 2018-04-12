# coding=utf-8

import re

from comply.rules.comments.pattern import COMMENT_BLOCK_PATTERN, COMMENT_LINE_PATTERN
from comply.rules.functions.pattern import FUNC_BODY_PATTERN

from comply.util.scope import depth


def strip_comments(text: str, patterns: list) -> str:
    """ Remove any comments matching provided patterns from a text.

        Entire comment is replaced by whitespace, leaving linebreaks in place.
    """

    stripped = text

    for pattern in patterns:
        comment_match = re.search(pattern, stripped)

        while comment_match is not None:
            comment = comment_match.group(0)

            replacement = ''

            for c in comment:
                if c in ['\r', '\n']:
                    replacement += c
                else:
                    replacement += ' '

            from_index = comment_match.start()
            to_index = comment_match.end()

            stripped = stripped[:from_index] + replacement + stripped[to_index:]

            comment_match = re.search(pattern, stripped)

    return stripped


def strip_any_comments(text: str) -> str:
    """ Remove both line- and block-style comments from a text. """

    return strip_comments(text, [COMMENT_BLOCK_PATTERN, COMMENT_LINE_PATTERN])


def strip_line_comments(text: str) -> str:
    """ Remove any line-style comments from a text. """

    return strip_comments(text, [COMMENT_LINE_PATTERN])


def strip_block_comments(text: str) -> str:
    """ Remove any block-style comments from a text. """

    return strip_comments(text, [COMMENT_BLOCK_PATTERN])


def strip_function_bodies(text: str) -> str:
    """ Remove any function bodies from a text.

        Any stripped line is replaced by a newline, additonally some special rules are applied:

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

        # leave newlines in place to ensure that line numbering remains correct
        replacement = '\n' * body.count('\n')

        if leave_braces_behind:
            # leave behind a collapsed function body
            replacement = '{}' + replacement

        from_index = body_match.start()
        to_index = body_match.end()

        stripped = stripped[:from_index] + replacement + stripped[to_index:]

        body_match = re.search(FUNC_BODY_PATTERN, stripped)

    return stripped


def strip_literals(text: str) -> str:
    """ Remove any string literals from a text.

        Stripped characters are replaced with whitespace; literal markers are left behind.

        For example:

          "A bunch of text", if found, becomes:
          "               "
    """

    stripped = text

    # match string literals, allowing escaped (\") quotes inside
    pattern = re.compile(r'(?<!\')\"([^\"\\]*(?:\\.[^\"\\]*)*)\"(?!\')')

    for match in pattern.finditer(stripped):
        literal = match.group(1)

        replacement = ' ' * len(literal)

        from_index = match.start(1)
        to_index = match.end(1)

        # note that we're doing an iterative search *while* we're modifying the text we're
        # matching on; this works out because the number of characters always remain the same
        # (i.e. we're just replacing with whitespace)
        stripped = stripped[:from_index] + replacement + stripped[to_index:]

    return stripped
