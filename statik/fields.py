# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from copy import copy

from statik.errors import *

__all__ = [
    'StatikModelField',
    'StatikDateTimeField',
    'StatikStringField',
    'StatikIntegerField',
    'StatikBooleanField',
    'StatikContentField',
    'StatikTextField',
    'StatikForeignKeyField',
    'StatikManyToManyField',
    'construct_field',
]


class StatikModelField(object):
    """Base class for all Statik model fields."""

    def __init__(self, name, field_type, **kwargs):
        self.name = name
        self.field_type = field_type
        # additional field parameters
        self.params = kwargs

    def __repr__(self):
        return "%s(name=%s, field_type=%s, params=%s)" % (
            self.__class__.__name__, self.name, self.field_type, self.params
        )


class StatikDateTimeField(StatikModelField):
    def __init__(self, name, **kwargs):
        super(StatikDateTimeField, self).__init__(name, 'DateTime', **kwargs)


class StatikStringField(StatikModelField):
    def __init__(self, name, **kwargs):
        super(StatikStringField, self).__init__(name, 'String', **kwargs)


class StatikTextField(StatikModelField):
    def __init__(self, name, **kwargs):
        super(StatikTextField, self).__init__(name, 'Text', **kwargs)


class StatikIntegerField(StatikModelField):
    def __init__(self, name, **kwargs):
        super(StatikIntegerField, self).__init__(name, 'Integer', **kwargs)


class StatikBooleanField(StatikModelField):
    def __init__(self, name, **kwargs):
        super(StatikBooleanField, self).__init__(name, 'Boolean', **kwargs)


class StatikContentField(StatikModelField):
    def __init__(self, name, **kwargs):
        super(StatikContentField, self).__init__(name, 'Content', **kwargs)


class StatikForeignKeyField(StatikModelField):
    def __init__(self, name, foreign_model, **kwargs):
        super(StatikForeignKeyField, self).__init__(name, foreign_model, **kwargs)
        self.back_populates = kwargs.get('back_populates', None)


class StatikManyToManyField(StatikModelField):
    def __init__(self, name, foreign_model, **kwargs):
        super(StatikManyToManyField, self).__init__(name, foreign_model, **kwargs)
        self.back_populates = kwargs.get('back_populates', None)


FIELD_TYPES = {
    'String': StatikStringField,
    'DateTime': StatikDateTimeField,
    'Integer': StatikIntegerField,
    'Boolean': StatikBooleanField,
    'Content': StatikContentField,
    'Text': StatikTextField,
}


def construct_field(model_name, field_name, field_type, all_models, **kwargs):
    """Helper function to build a field from the given field name and
    type.

    Args:
        model_name: The name of the model for which we're building this field.
        field_name: The name of the field to build.
        field_type: A string indicator as to which field type must be built.
        all_models: A list containing the names of all of the models, which
            will help us when building foreign key lookups.
    """
    field_type_parts = field_type.split('->')
    _field_type = field_type_parts[0].strip().split('[]')[0].strip()
    back_populates = field_type_parts[1].strip() if len(field_type_parts) > 1 else None
    error_context = kwargs.pop('error_context', StatikErrorContext())
    _kwargs = copy(kwargs)
    _kwargs['back_populates'] = back_populates

    if _field_type not in FIELD_TYPES and _field_type not in all_models:
        raise InvalidFieldTypeError(
            model_name,
            field_name,
            context=error_context
        )

    if _field_type in FIELD_TYPES:
        return FIELD_TYPES[_field_type](field_name, **_kwargs)

    if field_type_parts[0].strip().endswith('[]'):
        return StatikManyToManyField(field_name, _field_type, **_kwargs)

    return StatikForeignKeyField(field_name, _field_type, **_kwargs)
