# coding=utf-8

from comply.rules.rule import *


class NoSpaceName(Rule):
    """ Avoid whitespace in filenames.

    Mostly a matter of convention, but helps in avoiding issues when interacting with external
    tools.
    """

    def __init__(self):
        Rule.__init__(self, name='no-space-name',
                      description='Avoid whitespace in filenames',
                      suggestion='Replace whitespaces with underscores (e.g. \'{filename}\').')

    def collect(self, file: CheckFile):
        if ' ' in file.filename:
            suggested_filename = file.filename.replace(' ', '_') + file.extension

            offender = self.violate(file.line_number_at_top(),
                                    meta={'filename': suggested_filename})

            return [offender]

        return []

    @property
    def severity(self):
        return RuleViolation.ALLOW

    @property
    def collection_hint(self):
        return RuleViolation.ONCE_PER_FILE

    @property
    def triggering_filename(self):
        return 'a filename.c'

    @property
    def triggers(self):
        return ['▶']  # any content will trigger due to the assumed filename
