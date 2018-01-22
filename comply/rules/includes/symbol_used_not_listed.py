# coding=utf-8

from comply.rule import Rule, RuleViolation


class SymbolUsedNotListed(Rule):
    def __init__(self):
        Rule.__init__(self, name='symbol-used-not-listed',
                      description='Used symbols should be listed as required.',
                      suggestion='Add symbol \'{0}\' to list.')

    def collect(self, text: str, filename: str, extension: str) -> list:
        return []
