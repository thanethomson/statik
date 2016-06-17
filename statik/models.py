# -*- coding:utf-8 -*-

import yaml

from statik.common import YamlLoadable
from statik.fields import *
from statik.utils import extract_filename
from statik.errors import *

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'StatikModel'
]


class StatikModel(YamlLoadable):
    """Represents a single model in our Statik project."""

    RESERVED_FIELD_NAMES = set([
        'name', 'model_names', 'field_names', 'content_field',
        'filename', 'backrefs',
    ])

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
        self.backrefs = {}

        # build up all of our fields from the model configuration
        for field_name, field_type in self.vars.items():
            if field_type == 'Content':
                if self.content_field is not None:
                    raise ValueError("Only one \"Content\" field is allowed per model (%s)" % self.name)
                self.content_field = field_name

            new_field_name = field_name.replace('-', '_')

            # some reserved field names
            if new_field_name in StatikModel.RESERVED_FIELD_NAMES:
                raise ReservedFieldNameError("Field name \"%s\" is reserved for internal use and cannot be used on a model" % new_field_name)

            self.field_names.append(new_field_name)
            setattr(
                self,
                new_field_name,
                construct_field(new_field_name, field_type, self.model_names)
            )

    def get_backrefs(self):
        """Finds all of the fields in this model with back-populates
        references.

        Returns:
            A dictionary, indexed by foreign model name, where each value is
            the name of the back-populates reference field.
        """
        backrefs = {}
        for field_name in self.field_names:
            field = getattr(self, field_name)
            if isinstance(field, StatikForeignKeyField) or isinstance(field, StatikManyToManyField):
                if field.back_populates is not None:
                    backrefs[field.field_type] = field.back_populates
        logger.debug("Backrefs for model %s: %s" % (self.name, backrefs))
        return backrefs

    def track_backref(self, from_model_name, backref):
        self.backrefs[from_model_name] = backref
