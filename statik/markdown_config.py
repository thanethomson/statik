# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from six import iteritems
from copy import copy

from statik.errors import *

__all__ = [
    'MarkdownConfig'
]


class MarkdownConfig(object):

    DEFAULT_MARKDOWN_EXTENSIONS = [
        'markdown.extensions.fenced_code',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.footnotes'
    ]

    def __init__(self, markdown_params=None, error_context=None):
        self.error_context = error_context or StatikErrorContext()
        markdown_params = markdown_params or dict()
        if not isinstance(markdown_params, dict):
            raise ProjectConfigurationError(
                message="Markdown configuration parameters must be a dictionary.",
                context=error_context
            )

        permalinks_config = markdown_params.get('permalinks', dict())

        self.enable_permalinks = permalinks_config.get('enabled', False)
        if self.enable_permalinks in {"true", "1", 1}:
            self.enable_permalinks = True
        elif self.enable_permalinks in {"false", "0", 0}:
            self.enable_permalinks = False

        self.permalink_text = permalinks_config.get('text', "¶")
        self.permalink_class = permalinks_config.get('class', None)
        self.permalink_title = permalinks_config.get('title', None)

        # Required list of Markdown extensions
        self.extensions = copy(MarkdownConfig.DEFAULT_MARKDOWN_EXTENSIONS)

        # Configuration for the markdown extensions
        self.extension_config = {}
        extension_list = markdown_params.get('extensions', [])

        # if it's a dictionary, first convert it to our list notation
        if isinstance(extension_list, dict):
            extension_list = []
            for ext_package, config in iteritems(markdown_params['extensions']):
                extension_list.append({ext_package: config})

        # Try to load extensions as requested by config
        for extension in extension_list:
            if isinstance(extension, dict):
                ext_package, config = next(iter(extension.keys())), next(iter(extension.values()))
            else:
                ext_package, config = extension, None

            if ext_package not in self.extensions:
                self.extensions.append(ext_package)

            if config is not None: 
                if ext_package in self.extension_config:
                    self.extension_config[ext_package].update(config)
                else:
                    self.extension_config[ext_package] = config

    def __repr__(self):
        return ("MarkdownConfig(enable_permalinks=%s, permalink_text=%s, permalink_class=%s, " +
                "permalink_title=%s, extensions=%s, extension_config=%s)") % (
            self.enable_permalinks,
            self.permalink_text,
            self.permalink_class,
            self.permalink_title,
            self.extensions,
            self.extension_config
        )
