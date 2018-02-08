# coding=utf-8


def depth(index: int, text: str):
    """ Determine scope depth at a character index. """

    depth_count = 0

    for c in text[:index]:
        if c == '{':
            depth_count += 1
        elif c == '}':
            depth_count -= 1

    return depth_count
