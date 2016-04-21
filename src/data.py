# -*- coding:utf-8 -*-
"""
Data management for Statik.
"""

import logging
import json
import os.path
import markdown
import sqlite3

import utils
from exceptions import *

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
        # model dependencies (foreign key references)
        model_deps = {}
        # model table creation SQL statements
        create_sql = {}

        # work out the dependency graph for the models
        for model_name, model in models.iteritems():
            create_sql[model_name] = model.generate_sql()
            model_deps[model_name] = model.get_foreign_classes()

        # the set of CREATE TABLE statements, in sequence so as to satisfy all
        # foreign key dependencies...
        create_sql_seq = []
        created = set()
        while len(create_sql_seq) < len(create_sql):
            # if we have no dependencies
            pass

        # open up the connection to our in-memory SQLite database
        logger.debug("Creating in-memory SQLite database...")
        self._conn = sqlite3.connect(":memory:")


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
            while (line = f.readline()):
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
                    if preamble_started:
                        preamble += line
                    else:
                        content += line

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
