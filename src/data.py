# -*- coding:utf-8 -*-
"""
Data management for Statik.
"""

import logging
import json
import os.path

import utils
from exceptions import *

logger = logging.getLogger(__name__)
__all__ = [
    "StatikInstance",
]


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
        _, ext = os.path.splitext(os.path.basename(filename))
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
        logger.debug("Loaded data as: %s" % utils.pretty(self.data))


    def _load_markdown(self, filename):
        """Loads the data for this instance from a Markdown file.

        The function assumes it will potentially find a JSON preamble containing
        field data for this instance. If the model has a field of type
        "content", the remainder of the Markdown content will be inserted as
        that field's value.

        Args:
            filename: The absolute path to the Markdown file.

        Returns:
            A dictionary containing the extracted data.
        """
