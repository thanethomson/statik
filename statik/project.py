# -*- coding:utf-8 -*-

import os.path

from statik.config import StatikConfig
from statik.utils import list_files


__all__ = [
    'StatikProject',
]


class StatikProject(object):

    def __init__(self, path):
        """Constructor.

        Args:
            path: The full filesystem path to the base of the project.
        """
        self.path = path
        self.config = StatikConfig(os.path.join(path, 'config.yml'))
        self.models = self._load_models()
        self.views = self._load_views()
        self._populate_db()

    def _load_models(self):
        model_files = list_files(os.path.join(path, 'models'), ['yml', 'yaml'])
        # get all of the models' names
        model_names = [list(os.path.splitext(os.path.basename(model_file)))[0] for model_file in model_files]
        result = {}
        for model_file in model_files:
            model_name = list(os.path.splitext(os.path.basename(model_file)))[0]
            result[model_name] = StatikModel(model_file, model_names=model_names)
