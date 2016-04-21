# -*- coding:utf-8 -*-
"""
High-level objects for representing Statik projects.
"""

import logging
import os.path
import json

import utils
from exceptions import *
from config import *
from models import *
from views import *

logger = logging.getLogger(__name__)

__all__ = [
    "StatikProject",
]


class StatikProject:
    """A complete Statik project.

    Provides an object representation of a Statik project that exposes
    a number of pieces of functionality.
    """

    def __init__(self, path, profile='production'):
        """Constructor.

        Args:
            path: The file system path (absolute or relative) of the project's
                base folder, in which to find the project's contents.
            profile: For which profile should we be building/configuring this
                project?
        """
        # first make sure that the path exists
        try:
            path = utils.get_abs_path(path)
        except Exception:
            raise InvalidPathException("Path is invalid: %s" % path)

        if not os.path.isdir(path):
            raise PathNotDirectoryException("Path is not a valid, accessible directory: %s" % path)

        self._path = path
        logger.debug("Using absolute path for project: %s" % path)
        self._profile = profile
        logger.debug("Loading project with profile: %s" % profile)

        # load up our config
        self.load_config()


    def load_config(self):
        """Attempts to (re)load the configuration file for this project."""
        # check for a configuration file
        config_path = os.path.join(self._path, "config.json")
        if not os.path.isfile(config_path):
            raise MissingConfigException("Missing \"config.json\" file in project path: %s" % self._path)

        logger.debug("Attempting to read project configuration from: %s" % config_path)
        config = utils.load_json_file(config_path)
        logger.debug("Instantiating StatikProject object with configuration: %s" % utils.pretty(config))
        self._config = StatikConfig(self._path, config)

        # figure out the main configuration options from the config
        self._name = self._config.get_project_name()
        logger.debug("Detected project name: %s" % self._name)

        # see what kinds of profiles we've got here
        self._profiles = self._config.get_profiles()
        logger.debug("Detected project profiles: %s" % utils.pretty(self._profiles))

        # get the base URL for this project
        self._base_url = self._config.get_base_url()
        logger.debug("Project base URL configured as: %s" % self._base_url)

        self._output_path = self._config.get_output_path()
        logger.debug("Project output path configured as: %s" % self._output_path)
        # if the path doesn't exist, try to create it
        if not os.path.isdir(self._output_path):
            logger.debug("Output path does not exist - attempting to create it")
            os.makedirs(self._output_path)
            logger.debug("Created output path: %s" % self._output_path)


    def build(self):
        """Builds the project based on the supplied configuration."""
        # work out our various project paths
        models_path = os.path.join(self._path, "models")
        data_path = os.path.join(self._path, "data")
        templates_path = os.path.join(self._path, "templates")
        views_path = os.path.join(self._path, "views")

        logger.debug("Configured project paths as follows:")
        logger.debug("  Models    : %s" % models_path)
        logger.debug("  Data      : %s" % data_path)
        logger.debug("  Templates : %s" % templates_path)
        logger.debug("  Views     : %s" % views_path)

        # we absolutely must have views and templates at the very least
        if not os.path.isdir(templates_path):
            raise PathNotDirectoryException("Templates path is inaccessible: %s" % templates_path)
        if not os.path.isdir(views_path):
            raise PathNotDirectoryException("Views path is inaccessible: %s" % views_path)

        # models organised by model name
        models = {}
        # data items organised by model name, and then dictionaries of
        # data entries for each model name organised by the entry's unique id
        data = {}

        # if we have models, load them
        if os.path.isdir(models_path):
            logger.info("Loading models...")
            models = self.load_models(models_path)

            # if we have data, load it, but only if we have models
            if os.path.isdir(data_path):
                logger.info("Loading data...")
                data = self.load_data(data_path, models)

        # load the views
        logger.info("Loading views...")
        view_config = self.load_views(views_path, template_path, models, data)

        # finally, write the output data from the view config
        logger.info("Writing output files...")
        self.write_output(view_config)
        logger.info("Done!")


    def load_models(self, path):
        """Loads the models' configuration from the specified path.

        Args:
            path: The absolute path in which to search for model files.

        Returns:
            A dictionary whose keys correspond to model names, and values
            correspond to StatikModel objects.
        """
        result = {}
        # first list all of the possible models in the folder
        model_files = utils.list_dir(path, ["json"])
        for model_file in model_files:
            logger.debug("Found model file: %s" % model_file)
            # try to load the model
            model = StatikModel(os.path.join(path, model_file))
            result[model.name] = model

        logger.info("Loaded %d model(s)" % len(result))
        return result


    def load_data(self, path, models):
        """Loads all necessary data from the specified path.

        Args:
            path: The absolute path in which to search for data files.
            models: The model data, preloaded.

        Returns:
            A dictionary whose keys correspond to model names, and values
            are also dictionaries, whose keys correspond to the unique IDs of
            the items and values correspond to dictionaries containing the
            key/value pairs (field/field content pairs) for each entry.
        """
        result = {}
        per_model_count = {}
        total_count = 0

        logger.debug("Loading data instances from path: %s" % path)

        for model_name, model in models.iteritems():
            cur_path = os.path.join(path, model_name)
            # first look in our data path for a folder corresponding to this model
            if os.path.isdir(cur_path):
                # initialise the dataset for this model
                result[model_name] = {}
                per_model_count[model_name] = 0

                logger.debug("Found data path for model: %s" % model_name)
                # find all of the data entries in here
                data_files = utils.list_dir(cur_path, ["json", "md", "markdown"])
                for data_file in data_files:
                    data_file_fullpath = os.path.join(cur_path, data_file)
                    # load the instance
                    inst = StatikInstance(model, data_file_fullpath)
                    # keep track of its data
                    result[model_name][inst.id] = inst.data

                    per_model_count[model_name] += 1
                    total_count += 1

        for model_name, count in per_model_count.iteritems():
            logger.debug("Loaded %d instance(s) of model %s" % (count, model_name))
        logger.info("Loaded %d instance(s) in total" % (total_count))

        logger.debug("Populating in-memory SQLite database...")

        return result


    def load_views(self, views_path, templates_path, models, data):
        """Loads the view configuration from the specified path.

        Args:
            path: The absolute filesystem path of a folder in which to find
                all of the view configurations for the project.

        Returns:
            A StatikViewConfig object containing the view and routing
            configuration for the project.
        """
        pass


    def write_output(self, view_config):
        """Writes all of the output files using the specified view
        configuration, using all of our other configured parameters.

        Args:
            view_config: The output from load_views()
        """
