# coding=utf-8


class Ellipsize:
    middle = 0
    start = 1
    end = 2
    ends = 3


def truncated(text: str, length: int=40, ellipsize: int=Ellipsize.middle, from_index: int=None):
    """ Return text truncated to exactly fit a given length.

        If text is already shorter than the target length, text returns as is.
    """

    if length >= len(text):
        # no need to truncate
        return text

    ellipsis_character = '...'

    if length <= len(ellipsis_character):
        # no room to ellipsize
        return text

    if ellipsize == Ellipsize.middle:
        i = int(length / 2 - len(ellipsis_character))
        j = int(length - i - len(ellipsis_character))

        return '{1}{0}{2}'.format(ellipsis_character, text[:j], text[-i:])

    # adjust truncation length to account for the ellipsis
    i = length - len(ellipsis_character)

    if ellipsize == Ellipsize.start:
        return ellipsis_character + text[len(text) - i:]
    if ellipsize == Ellipsize.end:
        return text[:i] + ellipsis_character
    if ellipsize == Ellipsize.ends:
        j = from_index if from_index is not None else int(len(text) / 2)
        k = int(length / 2 - len(ellipsis_character))

        if j + k <= len(text):
            return ellipsis_character + text[j - k:j + k] + ellipsis_character
        else:
            return ellipsis_character + text[j - k:]
