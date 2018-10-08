# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from slugify import slugify

import re
import yaml
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.util import etree

from statik.errors import *
from statik.utils import strip_el_text

import lipsum

__all__ = [
    'MarkdownYamlMetaExtension',
    'MarkdownPermalinkExtension',
    'MarkdownYamlMetaPreprocessor',
    'MarkdownPermalinkProcessor',
    'MarkdownLoremIpsumExtension',
    'MarkdownLoremIpsumProcessor'
]


class MarkdownYamlMetaExtension(Extension):

    def extendMarkdown(self, md):
        md.preprocessors.register(
            MarkdownYamlMetaPreprocessor(md),
            'yaml-meta',
            40
        )


class MarkdownPermalinkExtension(Extension):

    def __init__(self, *args, **kwargs):
        self.permalink_text = kwargs.pop('permalink_text', None)
        self.permalink_class = kwargs.pop('permalink_class', None)
        self.permalink_title = kwargs.pop('permalink_title', None)
        super(MarkdownPermalinkExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        md.treeprocessors.register(
            MarkdownPermalinkProcessor(
                md,
                permalink_text=self.permalink_text,
                permalink_class=self.permalink_class,
                permalink_title=self.permalink_title
            ),
            'permalink',
            0
        )


class MarkdownLoremIpsumExtension(Extension):

    def __init__(self, *args, **kwargs):
        self.error_context = kwargs.pop('error_context', StatikErrorContext())
        super(MarkdownLoremIpsumExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(
            MarkdownLoremIpsumProcessor(md, error_context=self.error_context),
            "lipsum",
            50
        )


class MarkdownYamlMetaPreprocessor(Preprocessor):

    def run(self, lines):
        result = []
        self.md.meta = {}

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
                    result.append(line)

            if len(yaml_lines) > 0:
                self.md.meta = yaml.safe_load(
                    '\n'.join(yaml_lines)
                )

        return result


def insert_permalinks(el, permalink_text=None, permalink_class=None, permalink_title=None):
    for child in el:
        if child.tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'}:
            permalink = etree.Element('a')

            # try to get any existing ID from the heading tag
            id = child.get('id', None)
            # if there is none, slugify the text of the heading tag
            if id is None:
                heading_text = strip_el_text(child, max_depth=3)
                id = slugify(heading_text.replace('\'', '').replace('"', ''))
                # apply the ID to the heading
                child.set('id', id)

            permalink.set('href', '#%s' % id)

            if permalink_class is not None:
                permalink.set('class', permalink_class)
            if permalink_title is not None:
                permalink.set('title', permalink_title)

            if permalink_text is not None:
                permalink.text = permalink_text

            child.append(permalink)

        # recursively insert permalinks
        insert_permalinks(
            child,
            permalink_text=permalink_text,
            permalink_class=permalink_class,
            permalink_title=permalink_title
        )


class MarkdownPermalinkProcessor(Treeprocessor):

    def __init__(self, *args, **kwargs):
        self.permalink_text = kwargs.pop('permalink_text', None)
        self.permalink_class = kwargs.pop('permalink_class', None)
        self.permalink_title = kwargs.pop('permalink_title', None)
        super(MarkdownPermalinkProcessor, self).__init__(*args, **kwargs)

    def run(self, root):
        insert_permalinks(
            root,
            permalink_text=self.permalink_text,
            permalink_class=self.permalink_class,
            permalink_title=self.permalink_title
        )


class MarkdownLoremIpsumProcessor(Preprocessor):

    # we search for a single command on a line
    REGEXP = re.compile(r"^!\(lipsum-(?P<kind>word[s]?|sentence[s]?|paragraph[s]?)(:(?P<count>\d+))?\)\w*$")
    GENERATORS = {
        "word": (lipsum.generate_words, 1),
        "words": (lipsum.generate_words, None),
        "sentence": (lipsum.generate_sentences, 1),
        "sentences": (lipsum.generate_sentences, None),
        "paragraph": (lipsum.generate_paragraphs, 1),
        "paragraphs": (lipsum.generate_paragraphs, None)
    }

    def __init__(self, *args, **kwargs):
        self.error_context = kwargs.pop('error_context', StatikErrorContext())
        super(MarkdownLoremIpsumProcessor, self).__init__(*args, **kwargs)

    def run(self, lines):
        new_lines = []
        for line in lines:
            m = self.REGEXP.match(line)
            if m is not None:
                kind = m.group('kind')
                gen, count = self.GENERATORS[kind]
                if m.group('count') is not None:
                    count = int(m.group('count'))
                if count is None:
                    raise SyntaxError("Missing \"count\" parameter for !(lipsum-%s) command" % kind)

                new_lines.extend(gen(count).split("\n"))
            else:
                new_lines.append(line)
        return new_lines
