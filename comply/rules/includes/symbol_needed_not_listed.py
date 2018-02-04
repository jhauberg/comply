# coding=utf-8

from comply.rules import Rule


class SymbolNeededNotListed(Rule):
    def __init__(self):
        Rule.__init__(self, name='symbol-needed-not-listed',
                      description='Used symbols should be listed as needed',
                      suggestion='Add symbol \'{0}\' to list.')

    def collect(self, text: str, filename: str, extension: str) -> list:
        return []
