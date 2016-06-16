# -*- coding:utf-8 -*-

import yaml

from statik.common import YamlLoadable
from statik.fields import *
from statik.utils import extract_filename
from statik.errors import *


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
            self.name = extract_filename(self.filename)
        else:
            raise MissingParameterError("Missing model name in model constructor")

        if 'model_names' not in kwargs:
            raise MissingParameterError("Missing list of model names in model constructor")
        self.model_names = kwargs['model_names']
        self.field_names = []
        # if this model has a Content field
        self.content_field = None

        # build up all of our fields from the model configuration
        for field_name, field_type in self.vars.items():
            if field_type == 'Content':
                if self.content_field is not None:
                    raise ValueError("Only one \"Content\" field is allowed per model (%s)" % self.name)
                self.content_field = field_name

            new_field_name = field_name.replace('-', '_')
            self.field_names.append(new_field_name)
            setattr(
                self,
                new_field_name,
                construct_field(new_field_name, field_type, self.model_names)
            )
