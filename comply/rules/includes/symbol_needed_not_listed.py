# coding=utf-8

from comply.rules import Rule


class SymbolNeededNotListed(Rule):
    def __init__(self):
        Rule.__init__(self, name='symbol-needed-not-listed',
                      description='Used symbols should be listed as needed',
                      suggestion='Add symbol \'{symbol}\' to list.',
                      expects_original_text=True)  # must use original text including comments
