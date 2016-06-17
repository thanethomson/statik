# -*- coding:utf-8 -*-

from statik.errors import InvalidFieldTypeError

__all__ = [
    'StatikModelField',
    'StatikDateTimeField',
    'StatikStringField',
    'StatikIntegerField',
    'StatikBooleanField',
    'StatikContentField',
    'StatikTextField',
    'StatikForeignKeyField',
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
        return ("<StatikModelField name=%s\n" +
                "                  field_type=%s\n" +
                "                  params=%s>") % (
                    self.name, self.field_type, self.params,
                )


class StatikDateTimeField(StatikModelField):
    def __init__(self, name, **kwargs):
        super().__init__(name, 'DateTime', **kwargs)


class StatikStringField(StatikModelField):
    def __init__(self, name, **kwargs):
        super().__init__(name, 'String', **kwargs)


class StatikTextField(StatikModelField):
    def __init__(self, name, **kwargs):
        super().__init__(name, 'Text', **kwargs)


class StatikIntegerField(StatikModelField):
    def __init__(self, name, **kwargs):
        super().__init__(name, 'Integer', **kwargs)


class StatikBooleanField(StatikModelField):
    def __init__(self, name, **kwargs):
        super().__init__(name, 'Boolean', **kwargs)


class StatikContentField(StatikModelField):
    def __init__(self, name, **kwargs):
        super().__init__(name, 'Content', **kwargs)


class StatikForeignKeyField(StatikModelField):
    def __init__(self, name, foreign_model, **kwargs):
        super().__init__(name, foreign_model, **kwargs)


FIELD_TYPES = {
    'String': StatikStringField,
    'DateTime': StatikDateTimeField,
    'Integer': StatikIntegerField,
    'Boolean': StatikBooleanField,
    'Content': StatikContentField,
    'Text': StatikTextField,
}


def construct_field(name, field_type, all_models, **kwargs):
    """Helper function to build a field from the given field name and
    type.

    Args:
        name: The name of the field to build.
        field_type: A string indicator as to which field type must be built.
        all_models: A list containing the names of all of the models, which
            will help us when building foreign key lookups.
    """

    if field_type not in FIELD_TYPES and field_type not in all_models:
        raise InvalidFieldTypeError("Invalid field type: %s" % field_type)

    if field_type in FIELD_TYPES:
        return FIELD_TYPES[field_type](name, **kwargs)

    return StatikForeignKeyField(name, field_type, **kwargs)
