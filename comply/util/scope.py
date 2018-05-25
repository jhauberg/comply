# coding=utf-8


def depth(index: int, text: str):
    """ Determine depth of scope at a character index.

        Return 0 if not inside any scope.

        Note that braces found inside comments or literals are not ignored and will be counted.
        Note that a scope does not have to be properly balanced for this to return its depth.

        For example, in the string 'a { b { c', the index of 'c' would have a depth of 2.
    """

    depth_count = 0

    for c in text[:index]:
        if c == '{':
            depth_count += 1
        elif c == '}':
            depth_count -= 1

    return depth_count
