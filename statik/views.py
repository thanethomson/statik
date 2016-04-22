# -*- coding:utf-8 -*-
"""
Code for handling Statik views.
"""

import logging
import json
import os.path
from copy import copy

import utils
from errors import *

logger = logging.getLogger(__name__)
__all__ = [
    'StatikViewConfig',
    'RenderedStatikView',
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
    """

    def __init__(self, filename, template_env, models={}, db=None):
        """Constructor.

        Builds the view configuration from the specified file.

        Args:
            filename: The full path to the file to be parsed.
            template_env: The templating system environment object.
            models: The pre-loaded StatikModel objects for the project.
            db: A reference to the StatikDatabase object for extracting data
                out of the database for this view.
        """
        logger.debug("Attempting to parse view configuration: %s" % filename)
        self._filename = filename
        self._env = template_env
        self._models = models
        self._db = db
        self._config = utils.load_json_file(filename)
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
            if not self._db:
                raise MissingDatabaseException("View specifies that it relates to a model, but no database is supplied: %s" % filename)

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
        self.template = self._env.get_template(self._config['template'])
        logger.debug("Using view template: %s" % self.template)

        self.data = {}
        if 'data' in self._config:
            if not isinstance(self._config['data'], dict):
                raise InvalidViewConfiguration("Invalid \"data\" object in view configuration: %s" % filename)

            self.data = self._config['data']
        logger.debug("Using view data: %s" % self.data)


    def render(self):
        """Computes rendered views from this configuration.

        Returns:
            An iterator of RenderedStatikView objects that can be used to
            write the final output HTML.
        """
        # if this is a model-oriented view
        if self.model:
            field_names = [field_name for field_name, _ in self.model.fields.iteritems()]
            field_names.append('id')
            # first fetch all of the instances of this model
            for obj in self._db.query_obj(
                "SELECT %s FROM %s" % (", ".join(field_names),
                    self.model.name), field_names):
                # yield a rendered view of this object
                yield self._render_for_obj(obj)

        else:
            # work out our relative path
            path = self._compute_path(self.path)
            ctx = copy(self.data)
            # run through our data to try to expand any potential database
            # queries
            for k, v in self.data.iteritems():
                if isinstance(v, dict):
                    # if we have a SQL query/expression here
                    if '$' in v:
                        # first make sure that it also supplies field names
                        if 'fields' not in v or not isinstance(v['fields'], list):
                            raise InvalidViewConfigException("Missing or invalid \"fields\" field in data for \"%s\" in view: %s" % (
                                k, self._filename
                            ))

                        # try to expand the query into a list of objects
                        objs = [o for o in self._db.query_obj(v['$'], v['fields'])]
                        # replace it in the context
                        ctx[k] = objs
            # render the template for this view, with our data
            yield RenderedStatikView(path, self.template.render(**ctx))


    def _compute_path(self, pathspec, data=None):
        """Computes a relative path for the specified path spec based on the
        current data in the view config.

        Args:
            pathspec: A string containing a plain relative URL path or a
                Jinja2 template string.
            data: The data with which to render the template. This defaults to
                this view configuration's "data" attribute.

        Returns:
            A string containing the computed path.
        """
        if data is None:
            data = self.data
        return self._env.from_string(pathspec).render(**data)


    def _render_for_obj(self, obj):
        """Internal helper function to render this view for the specified
        object.

        Args:
            obj: The object, an instance of this view's associated model, in
                dictionary form.

        Returns:
            A RenderedStatikView instance.
        """
        # populate the context with our data
        ctx = copy(self.data)
        # and the object, which will be addressed as the name of the model
        # with its first letter turned to lowercase
        ctx["%s%s" % (self.model.name[0].lower(), self.model.name[1:])] = obj
        # compute the path
        path = self._compute_path(self.path, data=ctx)
        return RenderedStatikView(path, self.template.render(**ctx))


class RenderedStatikView:
    """A Statik view that has been fully rendered.

    Attributes:
        path: The relative path of this rendered view.
        html: The actual HTML content for this view.
    """

    def __init__(self, path, html):
        """Constructor.

        Args:
            path: The relative path of this rendered view.
            html: The actual HTML content for this view.
        """
        self.path = path.strip('/')
        self.html = html
