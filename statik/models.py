# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from future.utils import iteritems

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

    def __init__(self, name=None, model_names=None, **kwargs):
        super(StatikModel, self).__init__(**kwargs)
        # if we're explicitly overriding a model name
        if name is not None:
            self.name = name
        elif self.filename is not None:
            # extract the model name from its filename
            self.name = extract_filename(self.filename)
        else:
            raise MissingParameterError("name", context=self.error_context)

        if model_names is None:
            raise MissingParameterError("model_names", context=self.error_context)
        self.model_names = model_names

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
        for field_name, field_type in iteritems(self.vars):
            if field_type == 'Content':
                if self.content_field is not None:
                    raise ModelError(
                        self.name,
                        message="Only one \"Content\" field is allowed per model.",
                        context=self.error_context
                    )
                self.content_field = field_name

            new_field_name = field_name.replace('-', '_')
            self.field_names.append(new_field_name)
            new_field = construct_field(
                self.name,
                new_field_name,
                field_type,
                self.model_names,
                error_context=self.error_context
            )
            self.fields[new_field_name] = new_field
            if isinstance(new_field, StatikForeignKeyField) or \
                    isinstance(new_field, StatikManyToManyField):
                self.foreign_models.add(new_field.field_type)
            logger.debug("Built field: %s.%s of type %s", self.name, field_name, new_field)

    def find_additional_rels(self, all_models):
        """Attempts to scan for additional relationship fields for this model based on all of the other models'
        structures and relationships.
        """
        for model_name, model in iteritems(all_models):
            if model_name != self.name:
                for field_name in model.field_names:
                    field = model.fields[field_name]
                    # if this field type references the current model
                    if field.field_type == self.name and field.back_populates is not None and \
                            (isinstance(field, StatikForeignKeyField) or isinstance(field, StatikManyToManyField)):
                        self.additional_rels[field.back_populates] = {
                            'to_model': model_name,
                            'back_populates': field_name,
                            'secondary': (model_name, field.field_type)
                                if isinstance(field, StatikManyToManyField) else None
                        }
                        logger.debug(
                            'Additional relationship %s.%s -> %s (%s)',
                            self.name,
                            field.back_populates,
                            model_name,
                            self.additional_rels[field.back_populates]
                        )
