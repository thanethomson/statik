# -*- coding:utf-8 -*-

import os.path
import yaml

from statik.common import YamlLoadable

import logging
logger = logging.getLogger(__name__)


class StatikConfig(YamlLoadable):
    """Encapsulates a configuration object for a Statik project.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_name = self.vars.get('project-name', 'Untitled project')
        self.base_path = self.vars.get('base-path', '/')
        # relative to the output folder
        self.assets_src_path = self.assets_dest_path = 'assets'
        if 'assets' in self.vars and isinstance(self.vars['assets'], dict):
            if 'source' in self.vars['assets'] and isinstance(self.vars['assets']['source'], str):
                self.assets_src_path = self.vars['assets']['source']

            if 'dest' in self.vars['assets'] and isinstance(self.vars['assets']['dest'], str):
                self.assets_dest_path = self.vars['assets']['dest']

        logging.debug("%s" % self)

    def __repr__(self):
        return ("<StatikConfig project_name=%s\n" +
                "              base_path=%s\n" +
                "              assets_src_path=%s\n"+
                "              assets_dest_path=%s>") % (
                    self.project_name, self.base_path, self.assets_src_path,
                    self.assets_dest_path
                )
