# -*- coding:utf-8 -*-
"""
Code for handling Statik views.
"""

import logging
import json
import os.path

import utils
from exceptions import *

logger = logging.getLogger(__name__)
__all__ = [
    'StatikViewConfig'
]


class StatikViewConfig:
    """Encapsulates the configuration for a single Statik view.

    Attributes:
        name: A name uniquely identifying this particular view.
        path: The path spec for the view - can be a simple string or a Jinja2
            template string. This excludes the base URL for the current
            profile.
        model: If this view is model-specific, this will contain a reference
            to a StatikModel object, otherwise it will be None.
        template: The name/path of the template to be applied to this view.
        data: Data-related configuration and prepopulation for this view.
        html: An optional complete HTML rendering of this particular view.
    """

    def __init__(self, filename, models={}):
        """Constructor.

        Builds the view configuration from the specified file.

        Args:
            filename: The full path to the file to be parsed.
            models: The pre-loaded StatikModel objects for the project.
        """
        logger.debug("Attempting to parse view configuration: %s" % filename)
        self._filename = filename

        self._config = {}
        with open(filename, 'rt') as f:
            self._config = json.load(f)

        logger.debug("Loaded view configuration as: %s" % utils.pretty(self._config))

        # check for a name
        if 'name' in self._config:
            if not isinstance(self._config['name'], basestring):
                raise InvalidViewConfigException("Parameter \"name\" must be a string, in view configuration: %s" % filename)
            self.name = self._config['name']
        else:
            # use the filename, without the file extension, as the view name
            self.name, _ = os.path.splitext(os.path.basename(filename))
        logger.debug("Using view name: %s" % self.name)

        # check for a path spec for the view
        if 'path' not in self._config or not isinstance(self._config['path'], basestring):
            raise InvalidViewConfigException("Missing or invalid \"path\" parameter in view configuration: %s" % filename)
        self.path = self._config['path']
        logger.debug("Using view path: %s" % self.path)

        self.model = None
        # if this is a model-oriented view
        if 'model' in self._config:
            if not isinstance(self._config['model'], basestring):
                raise InvalidViewConfigException("Invalid model parameter value in view configuration: %s" % filename)

            # check that the model exists
            if self._config['model'] not in self._models:
                raise InvalidViewConfigException("The specified model \"%s\" does not exist, in view configuration: %s" % (self.model, filename))

            # keep track of which model this references
            self.model = models[self._config['model']]
        logger.debug("Using view model: %s" % self.model)

        if 'template' not in self._config or not isinstance(self._config['template'], basestring):
            raise InvalidViewConfiguration("Missing or invalid \"template\" parameter in view configuration: %s" % filename)
        self.template = self._config['template']
        logger.debug("Using view template: %s" % self.template)

        self.data = {}
        if 'data' in self._config:
            if not isinstance(self._config['data'], dict):
                raise InvalidViewConfiguration("Invalid \"data\" object in view configuration: %s" % filename)

            self.data = self._config['data']
        logger.debug("Using view data: %s" % self.data)

        # no html yet - usually set in a parent view's render() method
        self.html = None


    def render(self, obj=None):
        """Computes a "rendered" version of this view object - a new
        RenderedStatikView object containing all of the necessary content to
        be able to actually turn it into an HTML output file.

        Args:
            obj: An optional instance of the model relating to this view.

        Returns:
            A RenderedStatikView object containing the "rendered" version of
            this view object.
        """
        if self.model is not None:
            if not obj:
                raise MissingInstanceException("View \"%s\" is a model-oriented view, but no instance was supplied for rendering" % self.name)

            # make sure that the object is an instance of our desired object
            if not isinstance(obj, dict) or 'model' not in obj or obj['model'] != self.model.name:
                raise InvalidInstanceException("View \"%s\" requires a model of type \"%s\"" % (self.name, self.model.name))

            # do the model-oriented rendering
            return self._render_for_instance(obj)

        # renders this view by way of the supplied data only
        return self._render()


    def _render_for_instance(self, obj):
        """Renders this view specifically for the given model instance.

        Args:
            obj: An instance of the model relevant to this view.

        Returns:
            A RenderedStatikView object containing the "rendered" version of
            this view object.
        """
        return None


    def _render(self):
        """Renders this view using only the data supplied in the configuration
        for the view.

        Returns:
            A RenderedStatikView object containing the "rendered" version of
            this view object.
        """
        return None
