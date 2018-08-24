# coding=utf-8

"""
This is a build script for generating the docs site for comply.
"""

import os
import sys
import datetime
import inspect
import textwrap
import platform
import random

from ctypes import CDLL, c_char_p, c_long
from typing import List

sys.path.append("..")  # required to import from the 'comply' package

import comply.rules

from comply.version import __version__
from comply.rules.rule import Rule, RuleViolation

sysname = platform.system()

if sysname == 'Darwin':
    libname = "libcmark.dylib"
elif sysname == 'Windows':
    libname = "cmark.dll"
else:
    libname = "libcmark.so"

cmark = CDLL(libname)

markdown = cmark.cmark_markdown_to_html
markdown.restype = c_char_p
markdown.argtypes = [c_char_p, c_long, c_long]

opts = 0  # cmark defaults


def md2html(text) -> str:
    if sys.version_info >= (3, 0):
        textbytes = text.encode('utf-8')
        textlen = len(textbytes)

        return markdown(textbytes, textlen, opts).decode('utf-8')
    else:
        textbytes = text
        textlen = len(text)

        return markdown(textbytes, textlen, opts)


def find_all_rules() -> List[Rule]:
    # find all rule subclasses
    rule_types = [rule_class for rule_class in Rule.__subclasses__()]

    for idx, rule_type in enumerate(rule_types):
        sub_rule_types = [rule_class for rule_class in rule_type.__subclasses__()]

        next_idx = idx + 1

        # extend types by any found sub-types; this is practically recursive, as the next
        # enumeration iteration will automatically hit the newly discovered sub-types and then
        # find any sub-sub-types from the sub-types, and so on, indefinitely
        rule_types[next_idx:next_idx] = sub_rule_types

    # convert types to names (strings)
    rule_type_names = [rule_type.__name__ for rule_type in rule_types]

    # will hold Rule-subclassed object instances
    rule_instances = []

    # find all sub-modules inside the .rules package
    # (mod[1] is module object- mod[0] is just the name)
    modules = [mod[1] for mod in inspect.getmembers(comply.rules, inspect.ismodule)]

    for rule_type_name in rule_type_names:
        # brute-force our way through each module until we find the one it belongs in
        # then instantiate it and hold on to it for later
        for rule_module in modules:
            try:
                rule_attr = getattr(rule_module, rule_type_name)
            except AttributeError:
                # the rule did not belong in this module
                pass
            else:
                # we found the right module
                rule_instances.append(rule_attr())

                break

    return rule_instances


def fill_rule_template(tmp: str, rule: Rule) -> str:
    docstring = rule.__doc__

    if docstring is None or len(docstring) == 0:
        docstring = ''

        print('Missing docstring for \'{rule}\''
              .format(rule=rule.name))

    if len(docstring) > 0:
        docstring = '    ' + docstring.strip()  # assume docstring indentation of 4 spaces
        docstring = textwrap.dedent(docstring)

    lines = docstring.split('\n', 1)
    descr = ''

    if len(lines) > 0:
        descr = lines[0]

    docstring = docstring[len(descr):]

    refs = ''
    refs_index = docstring.rfind('References:')

    if refs_index != -1:
        refs = docstring[refs_index:]
        docstring = docstring[:refs_index]

    refs = refs.replace('References:', '**References:**')
    refs = refs.strip()

    suggest = ('<div class="suggestion">' +
               md2html('`' +
                       rule.description + ' => ' +
                       rule.suggestion +
                       '`') +
               '</div>')

    docstring = md2html(docstring)
    descr = md2html(descr) + suggest
    refs = md2html(refs)

    if len(docstring) > 0:
        docstring = '<div class="reasoning">' + docstring + '</div>'

    if len(refs) > 0:
        refs = '<div class="references">' + refs + '</div>'

    severity = ('deny' if rule.severity > RuleViolation.WARN else
                ('warn' if rule.severity > RuleViolation.ALLOW else
                 'allow'))

    tmp = tmp.replace('{{ rule_description }}', descr)
    tmp = tmp.replace('{{ rule_reasoning }}', docstring)
    tmp = tmp.replace('{{ rule_references }}', refs)
    tmp = tmp.replace('{{ rule_name }}', rule.name)
    tmp = tmp.replace('{{ rule_severity }}', severity)

    return tmp


template_path = 'base/index.html'
output_path = 'index.html'

rule_templates_path = 'base/rules'

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

rule_templates = [file for file in os.listdir(rule_templates_path) if not file.startswith('.')]
rule_templates = sorted(rule_templates)

rules = find_all_rules()

if len(rules) == 0:
    sys.exit('No rules found.')

# shuffle the list of rules into an interesting/random order:
# first, sort rules to ensure that the list is ordered the same every time
rules.sort(key=lambda r: r.name)
# then shuffle after applying a constant seed that produce the 'interesting' result
random.seed(12345)
random.shuffle(rules)

last_rule_index = len(rules) - 1

num_rules = 0

allow_overrides = True

for i, rule in enumerate(rules):
    rule_path = 'base/rule.html'

    if allow_overrides:
        if rule.name in [os.path.splitext(path)[0] for path in rule_templates]:
            rule_path = os.path.join(rule_templates_path, rule.name + '.html')

            print('Overriding template for \'{rule}\' => \'{template}\''
                  .format(rule=rule.name,
                          template=rule_path))

    try:
        rule_template_file = open(rule_path)
    except IOError:
        print('Template file \'{template}\' could not be read.'
              .format(template=rule_path))
    else:
        with rule_template_file:
            rule_template = rule_template_file.read()
            rule_template = fill_rule_template(rule_template, rule)

            if i != last_rule_index:
                # append template field at end so we can continue adding rule blocks
                rule_template = rule_template + '\n{{ rules }}'

            template = template.replace('{{ rules }}', rule_template)

            num_rules += 1

template = template.replace('{{ rules_count }}', str(num_rules))

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
