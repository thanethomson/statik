# -*- coding:utf-8 -*-

from statik.common import YamlLoadable
from statik.utils import underscore_var_names

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'StatikConfig',
]


class StatikConfig(YamlLoadable):
    """Encapsulates a configuration object for a Statik project.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_name = self.vars.get('project-name', 'Untitled project')
        self.base_path = self.vars.get('base-path', '/')
        self.encoding = self.vars.get('encoding')
        # relative to the output folder
        self.assets_src_path = self.assets_dest_path = 'assets'
        if 'assets' in self.vars and isinstance(self.vars['assets'], dict):
            if 'source' in self.vars['assets'] and isinstance(self.vars['assets']['source'], str):
                self.assets_src_path = self.vars['assets']['source']

            if 'dest' in self.vars['assets'] and isinstance(self.vars['assets']['dest'], str):
                self.assets_dest_path = self.vars['assets']['dest']

        self.context_static = {}
        self.context_dynamic = {}

        if 'context' in self.vars and isinstance(self.vars['context'], dict):
            if 'static' in self.vars['context'] and isinstance(self.vars['context']['static'], dict):
                self.context_static = underscore_var_names(self.vars['context']['static'])

            if 'dynamic' in self.vars['context'] and isinstance(self.vars['context']['dynamic'], dict):
                self.context_dynamic = underscore_var_names(self.vars['context']['dynamic'])

        logging.debug("%s" % self)

    def __repr__(self):
        return ("<StatikConfig project_name=%s\n" +
                "              base_path=%s\n" +
                "              encoding=%s\n" +
                "              assets_src_path=%s\n" +
                "              assets_dest_path=%s\n" +
                "              context_static=%s\n" +
                "              context_dynamic=%s>") % (
                    self.project_name, self.base_path, self.encoding, self.assets_src_path,
                    self.assets_dest_path, self.context_static, self.context_dynamic
                )
