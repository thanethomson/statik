# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from io import open

import os.path
import yaml
from markdown import Markdown

from statik.markdown_exts import *
from statik.utils import *
from statik.errors import *
from statik.markdown_config import MarkdownConfig

__all__ = [
    'YamlLoadable',
    'ContentLoadable',
]


class YamlLoadable(object):
    """Base class for objects that can be loaded from a YAML file or a
    YAML string, passed through to the constructor."""

    def __init__(self, *args, **kwargs):
        # default to UTF-8
        self.encoding = "utf-8"
        if len(args) > 0:
            self.filename = args[0]

            if 'encoding' in kwargs:
                self.encoding = kwargs['encoding']

            with open(self.filename, mode='rt', encoding=self.encoding) as f:
                self.file_content = f.read()

        elif 'from_string' in kwargs:
            self.filename = None
            self.file_content = kwargs['from_string']

        else:
            raise MissingParameterError("One or more missing arguments for constructor")

        # load the variables from the YAML file
        self.vars = yaml.load(self.file_content) if len(self.file_content) else {}
        if not isinstance(self.vars, dict):
            self.vars = {}
        else:
            # strip out any extra whitespace from the variables
            self.vars = dict_strip(self.vars)


class ContentLoadable(object):
    """Can provide functionality like the YamlLoadable class, but also supports
    loading content and metadata from a Markdown file.
    """
    def __init__(self, *args, **kwargs):
        self.vars = None
        self.content = None
        self.file_content = None
        self.file_type = kwargs.get('file_type', None)
        if self.file_type is not None:
            if self.file_type not in ['yaml', 'markdown']:
                raise ValueError("Invalid file type for content loadable: %s" % self.file_type)

        self.markdown_config = kwargs.get('markdown_config', None)
        self.encoding = "utf-8"

        if len(args) > 0:
            self.filename = args[0]

            if 'encoding' in kwargs:
                self.encoding = kwargs['encoding']

            if self.file_type is None:
                ext = list(os.path.splitext(self.filename))[1].lstrip('.')
                if ext not in ['yml', 'yaml', 'md', 'markdown']:
                    raise ValueError("File is not a YAML or Markdown-formatted file")
                self.file_type = 'yaml' if (ext in ['yml', 'yaml']) else 'markdown'

            with open(self.filename, mode='rt', encoding=self.encoding) as f:
                self.file_content = f.read()

        elif 'from_string' in kwargs:
            self.filename = None
            self.file_content = kwargs['from_string']

        elif 'from_dict' in kwargs:
            self.filename = None
            self.vars = kwargs['from_dict']

        else:
            raise MissingParameterError("One or more missing arguments for constructor")

        if 'name' in kwargs:
            self.name = kwargs['name']
        elif self.filename is not None:
            self.name = extract_filename(self.filename)
        else:
            raise MissingParameterError("Missing \"name\" argument for content loadable instance")

        # if it wasn't loaded from a dictionary
        if self.vars is None:
            if self.file_type is None:
                raise MissingParameterError("Missing file type parameter for content loadable")

            # if it's a YAML file
            if self.file_type == 'yaml':
                self.vars = yaml.load(self.file_content) if len(self.file_content) else {}
                if not isinstance(self.vars, dict):
                    self.vars = {}
            else:
                markdown_ext = [
                    MarkdownYamlMetaExtension(),
                    MarkdownLoremIpsumExtension()
                ]
                if self.markdown_config.enable_permalinks:
                    markdown_ext.append(
                        MarkdownPermalinkExtension(
                            permalink_text=self.markdown_config.permalink_text,
                            permalink_class=self.markdown_config.permalink_class,
                            permalink_title=self.markdown_config.permalink_title,
                        )
                    )
                markdown_ext.extend([
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.tables',
                    'markdown.extensions.toc',
                    'markdown.extensions.footnotes'
                ])
                md = Markdown(extensions=markdown_ext)
                self.content = md.convert(self.file_content)
                self.vars = md.meta

        if isinstance(self.vars, dict):
            self.vars = dict_strip(self.vars)
