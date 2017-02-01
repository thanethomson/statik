# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from copy import copy

from statik.errors import *
from statik.common import YamlLoadable
from statik.utils import underscore_var_names
from statik.markdown_config import MarkdownConfig
from statik.templating import DEFAULT_TEMPLATE_PROVIDERS

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'StatikConfig'
]


class StatikConfig(YamlLoadable):
    """Encapsulates a configuration object for a Statik project.
    """

    def __init__(self, *args, **kwargs):
        super(StatikConfig, self).__init__(*args, **kwargs)
        self.project_name = self.vars.get('project-name', 'Untitled project')
        self.base_path = self.vars.get('base-path', '/')
        self.encoding = self.vars.get('encoding', 'utf-8')
        self.theme = self.vars.get('theme', None)
        self.markdown_config = MarkdownConfig(self.vars.get('markdown', dict()))
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

        # work out our template engine precedence
        if 'templates' in self.vars and 'providers' in self.vars:
            if not isinstance(self.vars['templates']['providers'], list):
                raise TypeError("Template providers in project configuration must be a list")
            # validate our template providers
            self.template_providers = [provider for provider in self.vars['templates']['providers'] \
                                       if provider in DEFAULT_TEMPLATE_PROVIDERS]
        else:
            self.template_providers = copy(DEFAULT_TEMPLATE_PROVIDERS)

        if len(self.template_providers) == 0:
            raise NoSupportedTemplateProvidersError(
                "No supported template providers in project configuration. "
                "Available template providers: %s" % ", ".join(DEFAULT_TEMPLATE_PROVIDERS)
            )

        logging.debug("%s" % self)

    def __repr__(self):
        return ("<StatikConfig project_name=%s\n" +
                "              base_path=%s\n" +
                "              encoding=%s\n" +
                "              theme=%s\n" +
                "              template_providers=%s\n" +
                "              assets_src_path=%s\n" +
                "              assets_dest_path=%s\n" +
                "              context_static=%s\n" +
                "              context_dynamic=%s>") % (
                    self.project_name,
                    self.base_path,
                    self.encoding,
                    self.theme,
                    self.template_providers,
                    self.assets_src_path,
                    self.assets_dest_path,
                    self.context_static,
                    self.context_dynamic
                )
