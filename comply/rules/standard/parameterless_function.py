# coding=utf-8

import re

from comply.rules.standard.ambiguous_function import AmbiguousFunction
from comply.rules.patterns import FUNC_IMPL_PATTERN


class ParameterlessFunction(AmbiguousFunction):
    """ Always specify parameters as `void` if a function implementation takes zero parameters.

    Technically, this is not required for the compiler to do its job, but being explicit helps in
    keeping a clear and consistent interface.
    """

    def __init__(self):
        AmbiguousFunction.__init__(self)

        self.name = 'paramless-func'
        self.description = 'Parameterless function does not specify parameters as \'void\''
        self.pattern = re.compile(FUNC_IMPL_PATTERN)

    @property
    def triggers(self):
        return [
            'void ↓func() { ... }'
        ]

    @property
    def nontriggers(self):
        return [
            'void func(void) { ... }'
        ]
