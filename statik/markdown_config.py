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
