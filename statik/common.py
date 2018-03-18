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

    def __init__(self, filename=None, from_string=None, encoding='utf-8', error_context=None):
        # default to UTF-8
        self.encoding = encoding
        self.file_content = None
        self.error_context = error_context or StatikErrorContext()
        self.error_context.update(filename=filename)

        if filename is not None:
            self.filename = filename

            with open(self.filename, mode='rt', encoding=self.encoding) as f:
                self.file_content = f.read()

        elif from_string is not None:
            self.filename = None
            self.file_content = from_string

        else:
            raise MissingParameterError("filename", "from_string")

        # load the variables from the YAML file
        self.vars = yaml.safe_load(self.file_content) if self.file_content else {}
        if not isinstance(self.vars, dict):
            self.vars = {}
        else:
            # strip out any extra whitespace from the variables
            self.vars = dict_strip(self.vars)


class ContentLoadable(object):
    """Can provide functionality like the YamlLoadable class, but also supports
    loading content and metadata from a Markdown file.
    """
    def __init__(self, filename=None, file_type=None, from_string=None, from_dict=None,
            name=None, markdown_config=None, encoding='utf-8', error_context=None,
            content_field = None):
        self.vars = None
        self.content = None
        self.file_content = None
        self.file_type = file_type
        self.error_context = error_context or StatikErrorContext()
        self.error_context.update(filename=filename)

        if self.file_type is not None:
            if self.file_type not in ['yaml', 'markdown']:
                raise InternalError(
                    "Invalid file type for content loadable: %s" % self.file_type,
                    context=self.error_context
                )

        self.markdown_config = markdown_config
        self.encoding = encoding

        if filename is not None:
            self.filename = filename

            if self.file_type is None:
                ext = list(os.path.splitext(self.filename))[1].lstrip('.')
                if ext not in ['yml', 'yaml', 'md', 'markdown']:
                    raise StatikError(
                        message="The supplied file is not a YAML or Markdown-formatted file.",
                        context=self.error_context
                    )
                self.file_type = 'yaml' if (ext in ['yml', 'yaml']) else 'markdown'

            with open(self.filename, mode='rt', encoding=self.encoding) as f:
                self.file_content = f.read()

        elif from_string is not None:
            self.filename = None
            self.file_content = from_string

        elif from_dict is not None:
            self.filename = None
            self.vars = from_dict

        else:
            raise MissingParameterError(
                "filename", "from_string", "from_dict",
                context=self.error_context
            )
        if name is not None:
            self.name = name
        elif self.filename is not None:
            self.name = extract_filename(self.filename)
        else:
            raise MissingParameterError(
                "name", "filename",
                context=self.error_context
            )
        markdown_ext = [
                MarkdownYamlMetaExtension(),
                MarkdownLoremIpsumExtension(error_context=self.error_context)
            ]
        if self.markdown_config.enable_permalinks:
            markdown_ext.append(
                MarkdownPermalinkExtension(
                    permalink_text=self.markdown_config.permalink_text,
                    permalink_class=self.markdown_config.permalink_class,
                    permalink_title=self.markdown_config.permalink_title,
                )
            )
        markdown_ext.extend(self.markdown_config.extensions)
        md = Markdown(
            extensions=markdown_ext,
            extension_configs=self.markdown_config.extension_config
            )
        # if it wasn't loaded from a dictionary
        if self.vars is None:
            if self.file_type is None:
                raise MissingParameterError(
                    "file_type",
                    context=self.error_context
                )

            # if it's a YAML file
            if self.file_type == 'yaml':
                self.vars = yaml.safe_load(self.file_content) if self.file_content else {}
                if not isinstance(self.vars, dict):
                    self.vars = {}
            else:
                self.content = md.convert(self.file_content)
                self.vars = md.meta
        else:
            if (content_field is not None) and (content_field in self.vars):
                self.content = md.convert(self.vars[content_field])

        if isinstance(self.vars, dict):
            self.vars = dict_strip(self.vars)
