# coding=utf-8

import re

from comply.rules.comments.pattern import COMMENT_BLOCK_PATTERN


def strip_block_comments(text: str) -> str:
    """ Remove any block-style comments from a text. """

    stripped = text

    comment_pattern = COMMENT_BLOCK_PATTERN
    comment_match = re.search(comment_pattern, stripped)

    while comment_match is not None:
        comment = comment_match.group(0)

        from_index = comment_match.start()
        to_index = comment_match.end()

        # strip entire comment block, leaving newlines in place to ensure that
        # line numbering remains correct
        replacement = '<IGNORE>\n' * comment.count('\n')

        stripped = stripped[:from_index] + replacement + stripped[to_index:]

        comment_match = re.search(comment_pattern, stripped)

    return stripped
