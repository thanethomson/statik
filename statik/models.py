# -*- coding:utf-8 -*-

import yaml

from statik.common import YamlLoadable
from statik.fields import *


__all__ = [
    'StatikModel'
]


class StatikModel(YamlLoadable):
    """Represents a single model in our Statik project."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if we're explicitly overriding a model name
        if 'name' in kwargs:
            self.name = kwargs['name']
        elif self.filename is not None:
            # extract the model name from its filename
            self.name, _ = os.path.splitext(os.path.basename(self.filename))
        else:
            raise ValueError("Missing model name")

        if 'model_names' not in kwargs:
            raise ValueError("Missing list of model names in constructor")
        self.model_names = kwargs['model_names']

        # build up all of our fields from the model configuration
        for field_name, field_type in self.vars.items():
            new_field_name = field_name.replace('-', '_')
            setattr(
                self,
                new_field_name,
                construct_field(new_field_name, field_type, self.model_names)
            )
