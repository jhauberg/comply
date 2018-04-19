# coding=utf-8

import os
import sys
import datetime

sys.path.append("..")  # required to import __version__

from comply.version import __version__

template_path = 'base/index.html'
rules_path = 'base/rules'

output_path = 'index.html'

try:
    template_file = open(template_path)
except IOError:
    sys.exit('Template file \'{template}\' could not be read.'.format(
        template=template_path))
else:
    with template_file:
        template = template_file.read()

# format: April 14, 2018
date = '{:%B %d, %Y}'.format(datetime.date.today())

template = template.replace('{{ version }}', __version__)
template = template.replace('{{ date }}', date)

rules = [file for file in os.listdir(rules_path) if not file.startswith('.')]
rules = sorted(rules)

num_rules = 0

for i, rule_filename in enumerate(rules):
    rule_path = os.path.join(rules_path, rule_filename)

    with open(rule_path) as rule_file:
        rule_content = rule_file.read()

        if i != len(rules) - 1:
            # append template field at end so we can continue adding rule blocks
            rule_content = rule_content + '\n{{ rules }}'

        template = template.replace('{{ rules }}', rule_content)

        num_rules += 1

try:
    output_file = open(output_path, 'w')
except IOError:
    sys.exit('Output file \'{output}\' could not be created.'.format(
        output=output_path))
else:
    with output_file:
        output_file.write(template)

with open(output_path, 'w') as output_file:
    output_file.write(template)

print('Generated \'{output}\' ({number_of_rules} rules) successfully.'.format(
    output=output_path, number_of_rules=num_rules))
