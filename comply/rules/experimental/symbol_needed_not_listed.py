# coding=utf-8

from comply.rules.rule import *


class SymbolNeededNotListed(Rule):
    """ Always list used symbols as needed.<br/><br/>**_Not implemented._**

    If your code is using a symbol, but not explicitly telling where it got it from, you might have
    a hard time figuring out just how far your code reaches out.
    <br/><br/>
    See <tt>list-needed-symbols</tt>.
    """

    def __init__(self):
        Rule.__init__(self, name='symbol-needed-not-listed',
                      description='Used symbol \'{symbol}\' not listed as needed',
                      suggestion='Add symbol \'{symbol}\' to list.')

    @property
    def triggers(self):
        return [

        ]

    @property
    def nontriggers(self):
        return [

        ]
