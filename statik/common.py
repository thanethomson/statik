# -*- coding:utf-8 -*-

import yaml

__all__ = [
    'YamlLoadable',
]


class YamlLoadable(object):
    """Base class for objects that can be loaded from a YAML file or a
    YAML string, passed through to the constructor."""

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            self.filename = args[0]
            with open(self.filename, 'rt') as f:
                self.file_content = f.read()

        elif 'from_string' in kwargs:
            self.filename = None
            self.file_content = kwargs['from_string']

        else:
            raise ValueError("One or more missing arguments for constructor")

        # load the variables from the YAML file
        self.vars = yaml.load(self.file_content) if self.file_content else {}
