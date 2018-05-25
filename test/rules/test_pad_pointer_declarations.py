# coding=utf-8

from comply.rules.standard import PadPointerDeclarations
from comply.checking import check_text


RULE = PadPointerDeclarations()


def test_pad_pointer_decls_triggers():
    texts = ['char const *a = "asd";']

    for text in texts:
        result = check_text(text, [RULE])

        assert len(result.violations) == 1

        assert result.violations[0].where == (1, 12)
