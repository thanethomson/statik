# -*- coding:utf-8 -*-

import os.path
import jinja2

from statik.config import StatikConfig
from statik.utils import list_files, extract_filename
from statik.errors import *
from statik.models import StatikModel
from statik.views import StatikView
from statik.jinja2ext import *
from statik.database import StatikDatabase


__all__ = [
    'StatikProject',
]


class StatikProject(object):

    VIEWS_DIR = "views"
    MODELS_DIR = "models"
    TEMPLATES_DIR = "templates"
    DATA_DIR = "data"

    def __init__(self, path):
        """Constructor.

        Args:
            path: The full filesystem path to the base of the project.
        """
        self.path = path

    def generate(self, output_path=None, in_memory=False):
        """Executes the Statik project generator."""
        if output_path is None and not in_memory:
            raise ValueError("If project is not to be generated in-memory, an output path must be specified")

        self.models = self.load_models()
        self.template_env = self.configure_templates()
        self.views = self.load_views()
        self.template_env.statik_views = self.views
        self.db = self.load_db_data(self.models)

        in_memory_result = self.process_views()

        if in_memory:
            return in_memory_result
        else:
            # dump the in-memory output to files
            return self.dump_in_memory_result(in_memory_result)

    def configure_templates(self):
        template_path = os.path.join(self.path, StatikProject.TEMPLATES_DIR)
        if not os.path.isdir(template_path):
            raise MissingProjectFolderError(StatikProject.TEMPLATES_DIR, "Project is missing its templates folder")

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            extensions=['statik.jinja2ext.StatikUrlExtension']
        )
        env.filters['date'] = filter_datetime
        return env

    def load_models(self):
        models_path = os.path.join(self.path, StatikProject.MODELS_DIR)
        if not os.path.isdir(models_path):
            raise MissingProjectFolderError(StatikProject.MODELS_DIR, "Project is missing its models folder")

        model_files = list_files(models_path, ['yml', 'yaml'])
        # get all of the models' names
        model_names = [extract_filename(model_file) for model_file in model_files]
        models = {}
        for model_file in model_files:
            model_name = extract_filename(model_file)
            models[model_name] = StatikModel(
                os.path.join(models_path, model_file),
                name=model_name,
                model_names=model_names
            )

        return models

    def load_views(self):
        """Loads the views for this project from the project directory
        structure."""
        view_path = os.path.join(self.path, StatikProject.VIEWS_DIR)
        if not os.path.isdir(view_path):
            raise MissingProjectFolderError(StatikProject.VIEWS_DIR, "Project is missing its views folder")

        view_files = list_files(view_path, ['yml', 'yaml'])
        views = {}
        for view_file in view_files:
            view_name = extract_filename(view_file)
            views[view_name] = StatikView(
                os.path.join(view_path, view_file),
                name=view_name,
                models=self.models,
                template_env=self.template_env,
            )

        return views

    def load_db_data(self, models):
        data_path = os.path.join(self.path, StatikProject.DATA_DIR)
        if not os.path.isdir(data_path):
            raise MissingProjectFolderError(StatikProject.DATA_DIR, "Project is missing its data folder")

        return StatikDatabase(data_path, models)

    def process_views(self):
        """Processes the loaded views to generate the required output data."""
        output = {}
        for view_name, view in self.views.items():
            output.update(view.process(self.db))
        return output
