# coding=utf-8

import math


class Ellipsize:
    middle = 'mid'
    start = 'start'
    end = 'end'
    ends = 'ends'

    @staticmethod
    def options(at: str='mid', index: int=-1, character: str='...') -> (str, int, str):
        return at, index, character


def truncated(text: str, length: int = 40, options: (str, int, str)=Ellipsize.options()):
    """ Return text truncated to exactly fit a given length.

        If text is already shorter than the target length, text returns as is.
    """

    if length >= len(text):
        # no need to truncate
        return text

    ellipsis_type, marker_index, ellipsis_char = options
    ellipsis_length = len(ellipsis_char)

    if length <= ellipsis_length:
        # no room to ellipsize
        return text

    if ellipsis_type == Ellipsize.middle:
        i = (length / 2) - (ellipsis_length / 2)

        # note biased toward the left part (e.g. it may be 1 char longer than the right)
        a = math.ceil(i)
        b = math.floor(i)

        return text[:a] + ellipsis_char + text[-b:]

    # adjust truncation length to account for the ellipsis
    i = length - ellipsis_length

    if ellipsis_type == Ellipsize.start:
        return ellipsis_char + text[len(text) - i:]
    if ellipsis_type == Ellipsize.end:
        return text[:i] + ellipsis_char
    if ellipsis_type == Ellipsize.ends:
        j = marker_index if marker_index is not None else int(len(text) / 2)
        k = int((length / 2) - ellipsis_length)

        has_head = j - k > 0
        has_tail = j + k < len(text)

        if has_head and has_tail:
            return ellipsis_char + text[j - k:j + k] + ellipsis_char

        if has_head:
            distance_to_end = len(text) - j
            k = length - distance_to_end - ellipsis_length

            return ellipsis_char + text[j - k:]

        if has_tail:
            distance_to_start = j
            k = length - distance_to_start - ellipsis_length

            return text[:j + k] + ellipsis_char

        return text
