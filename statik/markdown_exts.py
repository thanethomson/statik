# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import yaml
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree

__all__ = [
    'MarkdownYamlMetaExtension',
    'MarkdownYamlMetaPreprocessor',
    'MarkdownPermalinkProcessor'
]


class MarkdownYamlMetaExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add(
            'yaml-meta',
            MarkdownYamlMetaPreprocessor(md),
            ">normalize_whitespace",
        )


class MarkdownYamlMetaPreprocessor(Preprocessor):

    def run(self, lines):
        result = []
        self.markdown.meta = {}

        if len(lines) > 1:
            yaml_lines = []
            if lines[0].strip() == '---':
                collecting_yaml = True
                start_line = 1
            else:
                collecting_yaml = False
                start_line = 0

            for line in lines[start_line:]:
                if collecting_yaml:
                    if line.strip() == '---':
                        collecting_yaml = False
                    else:
                        yaml_lines.append(line)
                else:
                    result.append(line.encode("ascii", "xmlcharrefreplace").decode("utf-8"))

            if len(yaml_lines) > 0:
                self.markdown.meta = yaml.load(
                    '\n'.join(yaml_lines).encode("ascii", "xmlcharrefreplace").decode("utf-8")
                )

        return result


def insert_permalinks(el, permalink_class=None, permalink_title=None):
    for child in el:
        if child.tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'}:
            permalink = etree.Element('a')

            if permalink_class is not None:
                permalink.set('class', permalink_class)
            if permalink_title is not None:
                permalink.set('title', permalink_title)

            permalink.set('href', '#%s')
            child.append(etree.Element('a'))


class MarkdownPermalinkProcessor(Treeprocessor):

    def __init__(self, **kwargs):
        self.config = {
            'permalink_class': None,
            'permalink_title': None
        }
        super(MarkdownPermalinkProcessor, self).__init__(**kwargs)

    def run(self, root):
        insert_permalinks(
            root,
            permalink_class=self.config['permalink_class'],
            permalink_title=self.config['permalink_title']
        )
