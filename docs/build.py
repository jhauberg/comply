# coding=utf-8

import os
import sys
import datetime
import inspect

sys.path.append("..")  # required to import from the 'comply' package

import comply.rules

from comply.version import __version__
from comply.rules import *

# find all rule subclasses
rule_types = [rule_class.__name__ for rule_class in Rule.__subclasses__()]

rules = []

# find all sub-modules inside the .rules package (mod[1] is module object- mod[0] is just the name)
modules = [mod[1] for mod in inspect.getmembers(comply.rules, inspect.ismodule)]

for rule_type in rule_types:
    # brute-force our way through each module until we find the one with this rule
    for rule_module in modules:
        try:
            rule_attr = getattr(rule_module, rule_type)
        except AttributeError as e:
            pass
        else:
            # so we can instantiate it and hold on to it for later
            rules.append(rule_attr())

            break

template_path = 'base/index.html'
rule_template_path = 'base/rules'

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

rule_templates = [file for file in os.listdir(rule_template_path) if not file.startswith('.')]
rule_templates = sorted(rule_templates)

num_rules = 0
num_excepted_rules = 0

for i, rule_filename in enumerate(rule_templates):
    rule_path = os.path.join(rule_template_path, rule_filename)
    rule_name, _ = os.path.splitext(rule_filename)

    rule_matches = [rule for rule in rules
                    if rule.name == rule_name]

    if len(rule_matches) == 0:
        print('Rule \'{rule}\' was not found in the rules package. '
              'Are you sure it\'s named right?'
              .format(rule=rule_name))

        num_excepted_rules += 1

        continue
    else:
        rule = rule_matches[0]

    with open(rule_path) as rule_file:
        rule_content = rule_file.read()

        rule_content = rule_content.replace('{{ rule_name }}', rule.name)

        if i != len(rule_templates) - num_excepted_rules - 1:
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
