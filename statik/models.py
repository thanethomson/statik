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
        # our model's fields
        self.fields = dict()
        self.field_names = []
        # if this model has a Content field
        self.content_field = None
        # additional back-reference relationships, indexed by field name
        self.additional_rels = dict()
        # all of the foreign models to which this model refers
        self.foreign_models = set()

        # build up all of our fields from the model configuration
        for field_name, field_type in self.vars.items():
            if field_type == 'Content':
                if self.content_field is not None:
                    raise ValueError("Only one \"Content\" field is allowed per model (%s)" % self.name)
                self.content_field = field_name

            new_field_name = field_name.replace('-', '_')
            self.field_names.append(new_field_name)
            new_field = construct_field(new_field_name, field_type, self.model_names)
            self.fields[new_field_name] = new_field
            if isinstance(new_field, StatikForeignKeyField) or isinstance(new_field, StatikManyToManyField):
                self.foreign_models.add(new_field.field_type)

    def find_additional_rels(self, all_models):
        """Attempts to scan for additional relationship fields for this model based on all of the other models'
        structures and relationships.
        """
        for model_name, model in all_models.items():
            if model_name != self.name:
                for field_name in model.field_names:
                    field = model.fields[field_name]
                    # if this field type references the current model
                    if field.field_type == self.name and field.back_populates is not None and \
                            (isinstance(field, StatikForeignKeyField) or isinstance(field, StatikManyToManyField)):
                        self.additional_rels[field.back_populates] = {
                            'to_model': model_name,
                            'back_populates': field_name,
                            'secondary':
                                (model_name, field.field_type) if isinstance(field, StatikManyToManyField) else None
                        }
                        logger.debug('Additional relationship %s.%s -> %s (%s)' % (
                            self.name,
                            field.back_populates,
                            model_name,
                            self.additional_rels[field.back_populates]
                        ))
