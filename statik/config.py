# -*- coding:utf-8 -*-

from copy import copy

from .errors import ProjectConfigurationError, NoSupportedTemplateProvidersError
from .common import YamlLoadable
from .utils import underscore_var_names
from .markdown_config import MarkdownConfig
from .external_database import ExternalDatabase
from .templating import DEFAULT_TEMPLATE_PROVIDERS

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

        self.external_database = None
        if 'external-database' in self.vars:
            self.external_database = ExternalDatabase(self.vars.get('external-database')).factory()
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
                raise ProjectConfigurationError(
                    message="Template providers in project configuration must be a list.",
                    context=self.error_context
                )
            # validate our template providers
            self.template_providers = [
                provider for provider in self.vars['templates']['providers'] \
                if provider in DEFAULT_TEMPLATE_PROVIDERS
            ]
        else:
            self.template_providers = copy(DEFAULT_TEMPLATE_PROVIDERS)

        if not self.template_providers:
            raise NoSupportedTemplateProvidersError(
                DEFAULT_TEMPLATE_PROVIDERS,
                context=self.error_context
            )

        # TODO: Add plugin architecture for deployment options
        self.deploy = self.vars.get('deploy', dict())
        if not isinstance(self.deploy, dict):
            raise ProjectConfigurationError(
                message="Deployment configuration must be a key/value pair map",
                context=self.error_context,
            )

        logging.debug("%s", self)

    def __repr__(self):
        return ("StatikConfig(project_name=%s, base_path=%s, encoding=%s, theme=%s, " +
                "template_providers=%s, assets_src_path=%s, assets_dest_path=%s, " +
                "context_static=%s, context_dynamic=%s, deploy=%s)") % (
                    self.project_name,
                    self.base_path,
                    self.encoding,
                    self.theme,
                    self.template_providers,
                    self.assets_src_path,
                    self.assets_dest_path,
                    self.context_static,
                    self.context_dynamic,
                    self.deploy,
                )
