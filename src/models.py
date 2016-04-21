# -*- coding:utf-8 -*-
"""
Model management for Statik.
"""

import logging
import json
import os.path
from datetime import datetime
import dateutil

import utils
from exceptions import *

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
            if field_type == "content":
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
            result[field_name] = content if field.field_type == "content" else \
                _obj.get(field_name, None)

            # if we have data in the field, try to force it to its intended type
            if result[field_name]:
                # if it's a date/time value
                if field.field_type in ["datetime", "date"]:
                    # try to convert it
                    dt = dateutil.parser.parse(result[field_name])
                    result[field_name] = dt if field.field_type == "datetime" else \
                        dt.date()

                elif field.field_type == "int":
                    result[field_name] = int(result[field_name])

                elif field.field_type in ["double", "float"]:
                    result[field_name] = float(result[field_name])

                elif field.field_type in ["string", "content"]:
                    result[field_name] = "%s" % result[field_name]

        return result


    def generate_sql(self):
        """Generates the SQL query to create a SQLite table to represent this
        model.

        Returns:
            A string containing the SQLite-compatible CREATE TABLE query.
        """
        # every field will have a unique id associated with it, because the
        # data item will have a unique filename
        fields_sql = ["id TEXT PRIMARY KEY NOT NULL"]
        foreign_keys = []
        for field_name, field in self.fields.iteritems():
            fields_sql.append("%s %s" % (field_name, field.get_sql_type()))
            if field.foreign_class:
                foreign_keys.append("FOREIGN KEY (%s) REFERENCES %s(id)" % (field_name, field.foreign_class))

        # we're going to just join these with commas right at the end of the
        # creation query
        fields_sql.extend(foreign_keys)

        query = "CREATE TABLE %s (%s)" % (self.name, ', \n'.join(fields_sql))
        logger.debug("Generated table creation query for model: %s" % self.name)
        logger.debug("  %s" % query)
        return query


    def get_foreign_classes(self):
        """Helper function to retrieve a list of all of the classes to which
        this class has foreign keys.

        Returns:
            A list containing the names of the models to which this class has
            foreign keys.
        """
        return [field.foreign_class for field_name, field in self.fields.iteritems() if field.foreign_class]


class StatikField:
    """Represents a single field in a model.

    Attributes:
        name: The name of this field.
        field_type: A string containing the type of field that this represents.
        foreign_class: If this field is a foreign key reference, this will
            contain the name of the foreign class it references. Otherwise
            it will contain None.
    """

    def __init__(self, model_name, field_name, field_type):
        """Constructor.

        Args:
            model_name: The name for the parent StatikModel object.
            field_name: The name for this Statik field.
            field_type: The field type for this field. Can be one of:
                "string", "int", "content", "datetime", "date", "float" or
                "fk|(Foreign class name)".
        """
        # mainly for debug logging
        self._model_name = model_name
        self.name = field_name

        if not field_type.startswith("fk|") and \
            field_type not in ['string', 'int', 'content', 'datetime', 'date', 'float']:
            raise InvalidFieldTypeException("Field \"%s\" for model \"%s\" cannot be of type: %s" % (name, model_name, field_type))
        self.field_type = field_type

        if self.field_type.startswith("fk|"):
            # extract the field type here
            self.foreign_class = self.field_type.split("|")[1]
            self.field_type = "fk"
        else:
            self.foreign_class = None


    def get_sql_type(self):
        """Constructs the SQL data type for this field type, as is required
        when creating a SQL table.

        Returns:
            A string containing the SQL fragment needed in the CREATE TABLE
            command to create this field.
        """
        if self.field_type in ["fk", "string", "content"]:
            return "TEXT"
        elif self.field_type == "int":
            return "INT"
        elif self.field_type == "datetime":
            return "DATETIME"
        elif self.field_type == "date":
            return "DATE"
        elif self.field_type == "float":
            return "DOUBLE"

        raise InvalidFieldTypeException("Field \"%s\" for model \"%s\" cannot be of type: %s" % (self.name, self._model_name, self.field_type))
