# -*- coding:utf-8 -*-
"""
Model management for Statik.
"""

import logging
import json
import os.path
from datetime import datetime
import dateutil.parser

import utils
from errors import *

logger = logging.getLogger(__name__)
__all__ = [
    "StatikModel",
    "StatikField",
]


class StatikModel:
    """Encapsulation of a model in the Statik project.

    Attributes:
        name: The class name for this model.
        fields: A dictionary containing a description of the fields for
            this model.
    """

    def __init__(self, filename):
        """Constructor.

        Loads the model configuration from the specified file.

        Args:
            filename: The name of the file from which to load the model
                configuration.
        """
        logger.debug("Attempting to load model configuration from: %s" % filename)
        self._filename = filename
        self._config = utils.load_json_file(filename)
        logger.debug("Loaded model configuration as: %s" % utils.pretty(self._config))

        if not isinstance(self._config, dict):
            raise InvalidModelConfigException("Invalid model configuration for model: %s" % filename)

        # extract the name of the model from the filename
        self.name, _ = os.path.splitext(os.path.basename(filename))
        logger.debug("Loaded model name as: %s" % self.name)

        # extract the fields from the model
        self.fields = {}
        content_count = 0
        for field_name, field_type in self._config.iteritems():
            if field_name == "_content":
                raise InvalidModelConfigException("Field name \"_content\" is reserved, and may not be used on models (from %s)" % self.name)

            self.fields[field_name] = StatikField(self.name, field_name, field_type)
            if field_type == "Content":
                content_count += 1
            logger.debug("  Added field %s of type: %s" % (field_name, field_type))

        if content_count > 1:
            raise InvalidModelConfigException("Model \"%s\" has more than 1 field of type \"content\" - only 1 is allowed" % self.name)


    def make_instance(self, obj):
        """Attempts to make an instance of this model from the given object,
        filling in non-existent attributes as None values.

        Note that this attempts to perform automatic conversion from the field
        values to the required data type, for example, date/time conversions.

        Args:
            obj: A dictionary containing some or none of the possible field
                values for this model.

        Returns:
            A dictionary containing keys corresponding only to the fields for
            this model, where missing fields will have None values.
        """
        # make sure we're working with a dictionary here
        _obj = obj if isinstance(obj, dict) else {}
        result = {}

        # if we have a value for the content field in this dictionary
        content = _obj.get('_content', None)

        for field_name, field in self.fields.iteritems():
            result[field_name] = content if field.field_type == "Content" else \
                _obj.get(field_name, None)

            # if we have data in the field, try to force it to its intended type
            if result[field_name]:
                # if it's a date/time value
                if field.field_type in ["DateTime", "Date"]:
                    # try to convert it
                    dt = dateutil.parser.parse(result[field_name])
                    result[field_name] = dt if field.field_type == "DateTime" else \
                        dt.date()

                elif field.field_type == "Integer":
                    result[field_name] = int(result[field_name])

                elif field.field_type in ["Double", "Float"]:
                    result[field_name] = float(result[field_name])

                elif field.field_type in ["String", "Content"]:
                    result[field_name] = "%s" % result[field_name]

        return result


    def generate_sql(self):
        """Generates the SQL query to create a SQLite table to represent this
        model.

        Returns:
            A 2-tuple, with the first value being the query (a string) to use
            to create the table for this model, and the second value being a
            dictionary of intermediate tables necessary for this table's
            functioning (for ManyToMany fields).
        """
        # every field will have a unique id associated with it, because the
        # data item will have a unique filename
        fields_sql = ["id TEXT PRIMARY KEY NOT NULL"]
        foreign_keys = []
        # for many-to-many relationships
        intermediate_tables = {}

        for field_name, field in self.fields.iteritems():
            sql_type = field.get_sql_type()
            if sql_type is not None:
                fields_sql.append("%s %s" % (field_name, field.get_sql_type()))
                if field.foreign_class:
                    foreign_keys.append("FOREIGN KEY (%s) REFERENCES %s(id)" % (field_name, field.foreign_class))

            elif field.field_type == "ManyToMany":
                table_names = sorted([field.name, field.foreign_class])
                _it = '_'.join(table_names)
                intermediate_tables[_it] = ("CREATE TABLE %(table_name)s (%(first_table)s_id, %(second_table)s_id, " + \
                    "FOREIGN KEY (%(first_table)s_id) REFERENCES %(first_table)s.id " + \
                    "FOREIGN KEY (%(second_table)s_id) REFERENCES %(second_table)s.id)") % \
                    {
                        'table_name': _it,
                        'first_table': table_names[0],
                        'second_table': table_names[1],
                    }

        # we're going to just join these with commas right at the end of the
        # creation query
        fields_sql.extend(foreign_keys)

        query = "CREATE TABLE %s (%s)" % (self.name, ', \n'.join(fields_sql))
        logger.debug("Generated table creation query for model: %s" % self.name)
        logger.debug("  %s" % query)
        return query, intermediate_tables


    def get_foreign_classes(self):
        """Helper function to retrieve a list of all of the classes to which
        this class has foreign keys.

        Returns:
            A list containing the names of the models to which this class has
            foreign keys.
        """
        return [field.foreign_class for field_name, field in self.fields.iteritems() if field.foreign_class]


    def get_related(self, models):
        """Returns info on this model's fields and the models to which those
        fields are related.

        Args:
            models: A dictionary indexed by model name from which to look up
                the related models.

        Returns:
            A dictionary indexed by field name with values corresponding to
            StatikModel instances of the foreign models linked to those fields.
        """
        return dict([
            (field_name, models[field.foreign_class]) \
                for field_name, field in self.fields.iteritems() \
                if field.foreign_class
        ])


class StatikField:
    """Represents a single field in a model.

    Attributes:
        name: The name of this field.
        field_type: A string containing the type of field that this represents.
        foreign_class: If this field is a foreign key reference, this will
            contain the name of the foreign class it references. Otherwise
            it will contain None.
        default_value: The default value of the field, if not specified.
        required: A boolean value indicating whether or not this field is
            required.
        back_ref: If this is a foreign key field, this attribute contains the
            name of the field on the foreign class that refers back to this
            model instance.
    """

    def __init__(self, model_name, field_name, field_type):
        """Constructor.

        Args:
            model_name: The name for the parent StatikModel object.
            field_name: The name for this Statik field.
            field_type: The field type for this field.
        """
        # mainly for debug logging
        self._model_name = model_name
        self.name = field_name
        self.field_type = None
        self.foreign_class = None
        self.default_value = None
        # fields are not required by default
        self.required = False
        self.back_ref = None

        _field_type = {}
        # if this is a complex type definition
        if isinstance(field_type, dict):
            type_name = field_type.get('type', None)
            # make sure we have a type
            if type_name is None:
                raise InvalidFieldTypeException("Field type is missing for field \"%s\" on model \"%s\"" % (field_name, model_name))

            _field_type = field_type
        else:
            _field_type = {'type': field_type}

        # validate the field type
        if _field_type['type'] not in ['String', 'Integer', 'Content', \
            'DateTime', 'Date', 'Float', 'OneToMany', 'ManyToOne', \
            'ManyToMany']:
            raise InvalidFieldTypeException("Field \"%s.%s\" cannot be of type: %s" % (model_name, field_name, field_type))

        self.field_type = _field_type['type']

        if self.field_type in ['OneToMany', 'ManyToOne', 'ManyToMany']:
            # extract the field type here
            self.foreign_class = _field_type.get('model', None)
            if not self.foreign_class:
                raise InvalidFieldTypeException("Field \"%s.%s\" is missing a foreign model reference" % (model_name, field_name))

        if 'required' in _field_type and isinstance(_field_type['required'], bool):
            self.required = _field_type['required']

        if 'default' in _field_type:
            self.default_value = _field_type['default']

        if 'backRef' in _field_type:
            self.back_ref = _field_type['backRef']


    def get_sql_type(self):
        """Constructs the SQL data type for this field type, as is required
        when creating a SQL table.

        Returns:
            A string containing the SQL fragment needed in the CREATE TABLE
            command to create this field. If this is a foreign key reference
            of type ManyToMany or OneToMany, this function will return None.
        """
        if self.field_type in ["ManyToOne"]:
            return "TEXT"
        elif self.field_type == "Integer":
            return "INT"
        elif self.field_type == "DateTime":
            return "DATETIME"
        elif self.field_type == "Date":
            return "DATE"
        elif self.field_type == "Float":
            return "DOUBLE"
        elif self.field_type in ["ManyToMany", "OneToMany"]:
            return None

        raise InvalidFieldTypeException("Field \"%s.%s\" cannot be of type: %s" % (self._model_name, self.name, self.field_type))


    def find_back_ref(self, foreign_model):
        """Attempts to establish this field's back-reference from the specified
        foreign model. If a back-reference is already specified, it validates
        the back-reference.

        Args:
            foreign_model: A StatikModel object representing the foreign model
                to which this field points.

        Raises:
            InvalidModelConfigException if there are too many possible options,
            or if there are no possible options, or if the back-reference is
            invalid.
        """
        potential_back_refs = []
        # compatible reference type combinations
        ref_type_combos = {
            'ManyToOne': 'OneToMany',
            'OneToMany': 'ManyToOne',
            'ManyToMany': 'ManyToMany',
        }
        # run through the foreign class' fields
        for foreign_field_name, foreign_field in foreign_model.fields.iteritems():
            # if it's a foreign key, the foreign key points back to this
            # model, and its type is compatible with this field's type
            if foreign_field.field_type in ref_type_combos and \
                foreign_field.foreign_class == self._model_name and \
                ref_type_combos[foreign_field.field_type] == self.field_type:
                potential_back_refs.append(foreign_field_name)

        if self.back_ref:
            if self.back_ref not in potential_back_refs:
                raise InvalidModelConfigException("Field \"%s.%s\" contains an invalid back-reference" % (
                    self._model_name, self.name,
                ))

        else:
            # if we have too many back-references
            if len(potential_back_refs) > 1:
                raise InvalidModelConfigException("Field \"%s.%s\" has too many potential back-references" % (
                    self._model_name, self.name,
                ))
            elif len(potential_back_refs) == 0:
                raise InvalidModelConfigException("Field \"%s.%s\" has no back-references" % (
                    self._model_name, self.name,
                ))

            # keep track of this back-reference
            logger.debug("Inferring back-reference for field \"%s.%s\" as \"%s.%s\"" % (
                model_name, field_name, field.foreign_class, potential_back_refs[0],
            ))
            self.back_ref = potential_back_refs[0]

        return self.back_ref
