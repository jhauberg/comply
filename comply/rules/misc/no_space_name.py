# coding=utf-8

from comply.rules import Rule, RuleViolation, CheckFile


class NoSpaceName(Rule):
    def __init__(self):
        Rule.__init__(self, name='no-space-name',
                      description='Avoid whitespace in filenames',
                      suggestion='Replace whitespaces with underscores (e.g. \'{filename}\').')

    def collect(self, file: CheckFile):
        if ' ' in file.filename:
            suggested_filename = file.filename.replace(' ', '_') + file.extension

            offender = self.violate(RuleViolation.at_top(),
                                    meta={'filename': suggested_filename})

            return [offender]

        return []

    @property
    def severity(self):
        return RuleViolation.ALLOW

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE
