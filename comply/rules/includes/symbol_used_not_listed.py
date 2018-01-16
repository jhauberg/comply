# coding=utf-8

from comply.rule import Rule, RuleOffender


class SymbolUsedNotListed(Rule):
    def __init__(self):
        Rule.__init__(self, name='symbol-used-not-listed',
                      description='Used symbols should be listed as required.',
                      suggestion='Add symbol \'{0}\' to list.')

    def offend(self, at: (int, int), offending_text: str, token: str=None) -> RuleOffender:
        return super().offend(at, offending_text, token)

    def collect(self, text: str) -> list:
        return []
