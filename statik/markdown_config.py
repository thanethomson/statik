# -*- coding: utf-8 -*-

from __future__ import unicode_literals

__all__ = [
    'MarkdownConfig'
]


class MarkdownConfig(object):

    def __init__(self, markdown_params=dict()):
        if not isinstance(markdown_params, dict):
            raise ValueError("Markdown configuration parameters must be a dictionary")

        permalinks_config = markdown_params.get('permalinks', dict())

        self.enable_permalinks = permalinks_config.get('enabled', False)
        if self.enable_permalinks in {"true", "1", 1}:
            self.enable_permalinks = True
        elif self.enable_permalinks in {"false", "0", 0}:
            self.enable_permalinks = False

        self.permalink_text = permalinks_config.get('text', "¶")
        self.permalink_class = permalinks_config.get('class', None)
        self.permalink_title = permalinks_config.get('title', None)

        # Required lsit of Markdown extensions
        self.extensions = [
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.toc',
            'markdown.extensions.footnotes'
        ]

        # Configuration for the markdown extensions
        self.extension_config = {}

        # Try to load in entensions requested by config
        for extention, config in markdown_params.get('extensions', dict()).items():
            if extention not in self.extensions:
                self.extensions.append(extention)

            if config is not None: 
                if extention in self.extension_config:
                    self.extension_config[extention].update(config)
                else:
                    self.extension_config[extention] = config

    def __repr__(self):
        return ("<MarkdownConfig enable_permalinks=%s\n" +
                "                permalink_text=%s\n" +
                "                permalink_class=%s\n" +
                "                permalink_title=%s>") % (
            self.enable_permalinks,
            self.permalink_text,
            self.permalink_class,
            self.permalink_title
        )
