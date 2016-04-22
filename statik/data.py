# -*- coding:utf-8 -*-
"""
Data management for Statik.
"""

import logging
import json
import os.path
import markdown
import sqlite3
from copy import copy

import utils
from errors import *

logger = logging.getLogger(__name__)
__all__ = [
    "StatikInstance",
    "StatikDatabase",
]


class StatikDatabase:
    """Provides an interface to an in-memory SQLite database through which we
    will manage our data model."""

    def __init__(self, models, data):
        """Constructor.

        Builds up the in-memory SQLite database from the specified models and
        data.

        Args:
            models: The models, loaded from a project.
            data: The data for the models, loaded from a project.
        """
        self._models = models
        # open up the connection to our in-memory SQLite database
        logger.debug("Creating in-memory SQLite database...")
        self._conn = sqlite3.connect(":memory:")
        logger.debug("Attempting to create SQLite database tables")
        try:
            self._create_tables()
        except Exception as e:
            logger.exception("Exception caught while attempting to create database tables")
            self.close()
            # re-throw the exception
            raise e

        logger.debug("Attempting to populate database with data")
        try:
            self._load_data(data)
        except Exception as e:
            logger.exception("Exception caught while attempting to populate database")
            self.close()
            # re-throw the exception
            raise e


    def _create_tables(self):
        """Internal function to create all of the necessary database tables for
        the current model configuration."""
        # model dependencies (foreign key references)
        model_deps = {}
        # model table creation SQL statements
        create_sql = {}
        # the set of CREATE TABLE statements, in sequence so as to satisfy all
        # foreign key dependencies...
        create_sql_seq = []
        created = set()

        # work out the dependency graph for the models
        for model_name, model in self._models.iteritems():
            create_sql[model_name] = model.generate_sql()
            model_deps[model_name] = model.get_foreign_classes()
            # if this model has no dependencies (yay!)
            if not model_deps[model_name]:
                create_sql_seq.append(create_sql[model_name])
                created.add(model_name)

        remaining_models = set(self._models.keys()) - created
        # now try to resolve the remaining models' dependencies
        while len(remaining_models) > 0:
            prev_remaining = len(remaining_models)

            _remaining_models = copy(remaining_models)
            # run through the models to see which of them we can create now
            for model_name in remaining_models:
                satisfied = True
                for dep in model_deps[model_name]:
                    if dep not in created:
                        satisfied = False

                if satisfied:
                    create_sql_seq.append(create_sql[model_name])
                    created.add(model_name)
                    _remaining_models.remove(model_name)

            remaining_models = _remaining_models

            # if we didn't make a dent in the remaining models list
            if len(remaining_models) == prev_remaining:
                raise CircularDependencyException("One of the following models has a circular dependency: %s" % utils.pretty(remaining_models))

        # create the database tables
        for query in create_sql_seq:
            self.execute(query)


    def _load_data(self, data):
        """Internal helper function to load the specified data into the
        in-memory SQLite database."""
        for model_name, instances in data.iteritems():
            for obj_id, obj in instances.iteritems():
                query, args = self.make_insert_query(
                    self._models[model_name],
                    obj,
                )
                self.execute(query, *args)


    def make_insert_query(self, model, obj):
        """Works out the query to insert the specified object, of the given
        model class, into the relevant database table.

        Args:
            model: The model to which the given object instance belongs.
            obj: A dictionary containing the relevant fields for the object
                instance.

        Returns:
            A 2-tuple containing the SQL query string and a list of field values
            to be inserted along with the query (can be an empty list).
        """

        field_names = ['id']
        field_names.extend([field_name for field_name, _ in model.fields.iteritems()])
        field_values = [obj.get(field_name) for field_name in field_names]

        query = "INSERT INTO %s (%s) VALUES (%s)" % (
            model.name,
            ",".join([field_name for field_name in field_names]),
            ",".join(["?" for f in field_names]),
        )

        return query, field_values


    def execute(self, query, *args):
        """Executes a simple, single SQL query.

        See https://docs.python.org/2/library/sqlite3.html for more details.

        Args:
            query: A string containing the SQL query.
            args: A variable-length array of arguments to pass to the query
                execution routine.

        Returns:
            An iterable object for retrieving the results.
        """
        logger.debug("Attempting to execute SQL query:")
        logger.debug("  %s" % query)
        logger.debug("With args: %s" % utils.pretty(args))
        return self._conn.execute(query, args)


    def query_obj(self, query, field_names):
        """Performs a SQL query, iterating through the result and trying to
        convert each row to a dictionary object with the specified field names.
        Yields results instead of returning them as a list, so one would need to
        iterate through the result to obtain all of the resulting objects.

        Args:
            query: The SQL query string to execute. Usually a SELECT query.
            field_names: A list of field names, in order, to be expected from
                each result.
        """
        for row in self.execute(query):
            _row = list(row)
            _obj = {}
            for i in range(len(_row)):
                _obj[field_names[i]] = _row[i]
            yield _obj


    def close(self):
        """Closes the current database connection."""
        self._conn.close()


class StatikInstance:
    """An instance of a particular Statik model.

    Attributes:
        data: A dictionary where keys correspond to model fields and values
            correspond to instance values for those fields.
    """

    def __init__(self, model, filename):
        """Constructor.

        Loads this instance of static model from the specified file.
        Automatically detects whether the file is a JSON file or Markdown
        file and processes it accordingly.

        Args:
            model: The StatikModel to which this instance belongs.
            filename: The absolute path of the data file from which to load
                the instance data.
        """
        self._model = model
        self._filename = filename

        logger.debug("Attempting to load data instance from: %s" % filename)
        instance_id, ext = os.path.splitext(os.path.basename(filename))
        ext = ext.lstrip(".")
        self._content = {}
        if ext in ["md", "markdown"]:
            self._content = self._load_markdown(filename)
        elif ext == "json":
            self._content = self._load_json(filename)
        else:
            raise UnsupportedDataFileException("Files of type \"%s\" are not supported (%s)" % (ext, filename))

        logger.debug("Loaded data content as: %s" % utils.pretty(self._content))
        self.data = model.make_instance(self._content)
        # set the ID as the base filename
        self.data['id'] = instance_id
        logger.debug("Loaded data as: %s" % utils.pretty(self.data))


    def _load_markdown(self, filename):
        """Loads the data for this instance from a Markdown file.

        The function assumes it will potentially find a JSON preamble containing
        field data for this instance. If the model has a field of type
        "content", the remainder of the Markdown content will be inserted as
        that field's value. Note that the Markdown content will be converted
        into HTML.

        Args:
            filename: The absolute path to the Markdown file.

        Returns:
            A dictionary containing the extracted data.
        """
        result = {}
        with open(filename, 'rt') as f:
            preamble = ''
            preamble_started = False
            preamble_ended = False

            content = ''

            # read the file line by line
            line = f.readline()
            while line:
                # if we're expecting the start or end of a JSON string
                if line.strip() == '===':
                    # if we haven't reached the end of the preamble yet
                    if not preamble_ended:
                        # if we've already started the preamble
                        if preamble_started:
                            # this must be the end of the preamble
                            preamble_ended = True
                        else:
                            # otherwise this is just the beginning of the preamble
                            preamble_started = True
                else:
                    if preamble_started and not preamble_ended:
                        preamble += line
                    else:
                        content += line

                # get the next line
                line = f.readline()

            logger.debug("Attempting to load data from preamble: %s" % preamble)
            # load the data from the preamble
            result = json.loads(preamble) if preamble else {}
            # process the Markdown content into HTML
            result['_content'] = markdown.markdown(content)

        return result


    def _load_json(self, filename):
        """Loads the data for this instance from the specified JSON file.

        Note that content can be supplied by specifying a "_content" object
        as part of the JSON object, and must adhere to the following
        structure:

        ```json
        {
            "otherField": "someValue",
            "_content": {
                "html": "<h1>Some HTML content here!</h1>"
                // An alternative to the above would be:
                // "markdown": "# Some HTML content here!"
            }
        }
        ```

        At present, only "html" and "markdown" are supported as content
        formats.

        Args:
            filename: The absolute path to the JSON file from which to read
                the data.

        Returns:
            A dictionary containing the extracted data.
        """
        result = utils.load_json_file(filename)

        # handle any content, if supplied
        if "_content" in result:
            if not isinstance(result["_content"], dict):
                raise InvalidDataException("If supplied, a \"_content\" entry must be an object (see %s)" % filename)

            if 'html' not in result['_content'] and 'markdown' not in result['content']:
                raise InvalidDataException("Invalid content format supplied in file: %s (must be \"html\" or \"markdown\")" % filename)

            # figure out the content
            result['_content'] = markdown.markdown(result['_content']['markdown']) \
                if 'markdown' in result['_content'] else result['_content']['html']

        return result
