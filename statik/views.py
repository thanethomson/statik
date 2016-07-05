# -*- coding:utf-8 -*-

import os.path

from copy import deepcopy

from statik.common import YamlLoadable
from statik.errors import MissingParameterError
from statik.utils import *

import logging

logger = logging.getLogger(__name__)

__all__ = [
    'StatikView',
]


class StatikView(YamlLoadable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # defaults
        self.complex = False
        self.path = None
        self.template = None
        self.path_template = None
        self.path_variable = None
        self.path_query = None
        self.context = kwargs.get('initial_context', dict())
        self.context_static = dict()
        self.context_dynamic = dict()
        self.context_for_each = dict()
        self.template_ext = '.html'
        self.default_output_filename = 'index'

        if 'name' in kwargs:
            self.name = kwargs['name']
        elif self.filename is not None:
            self.name = extract_filename(self.filename)
        else:
            raise MissingParameterError("Missing parameter \"name\" in view constructor")

        if 'models' not in kwargs:
            raise MissingParameterError("Missing parameter \"models\" in view constructor")
        # keep a reference to the models
        self.models = kwargs['models']

        if 'template_env' not in kwargs:
            raise MissingParameterError("Missing parameter \"template_env\" in view constructor")
        self.template_env = kwargs['template_env']

        self.configure()
        logger.debug('%s' % self)

    def __repr__(self):
        return ('<StatikView name=%s\n' +
                '            path=%s\n' +
                '            template=%s>\n') % (
                   self.name, self.path, self.template,
               )

    def configure(self):
        # process the parsed view variables
        if 'path' not in self.vars:
            raise MissingParameterError("Missing variable \"path\" in view: %s" % self.name)
        self.path = self.vars['path']

        # if it's a complex view
        if isinstance(self.path, dict):
            self.configure_complex_view(self.path)
        elif isinstance(self.path, str):
            self.configure_simple_view(self.path)
        else:
            raise ValueError("Unrecognised structure for \"path\" configuration in view: %s" % self.name)

        if 'template' not in self.vars:
            raise MissingParameterError("Missing variable \"template\" in view: %s" % self.name)
        template_filename, template_ext = os.path.splitext(self.vars['template'])
        if template_ext is None or len(template_ext) == 0:
            template_path = '%s.html' % self.vars['template']
            self.template_ext = '.html'
        else:
            template_path = self.vars['template']
            self.template_ext = template_ext
        logger.debug("Attempting to load template: %s" % template_path)
        self.template = self.template_env.get_template(template_path)

        self.configure_context()

    def configure_complex_view(self, path):
        if 'template' not in path:
            raise MissingParameterError(
                "Complex \"path\" variable must contain a \"template\" value in view: %s" % self.name)
        if 'for-each' not in path:
            raise MissingParameterError("Complex \"path\" variable must contain a \"for-each\" value in view: " +
                                        "%s" % self.name)
        if not isinstance(path['for-each'], dict) or len(path['for-each']) != 1:
            raise ValueError("Complex \"path\" variable's \"for-each\" value must be a single-valued dictionary " +
                             "in view: %s" % self.name)

        self.complex = True
        self.path_template = path['template']
        self.path_variable = list(path['for-each'].keys())[0]
        self.path_query = list(path['for-each'].values())[0]

    def configure_simple_view(self, path):
        self.complex = False

    def configure_context(self):
        if 'context' in self.vars:
            if 'static' in self.vars['context'] and isinstance(self.vars['context']['static'], dict):
                self.context_static = underscore_var_names(deepcopy(self.vars['context']['static']))

            if 'dynamic' in self.vars['context'] and isinstance(self.vars['context']['dynamic'], dict):
                self.context_dynamic = underscore_var_names(deepcopy(self.vars['context']['dynamic']))

            if 'for-each' in self.vars['context'] and isinstance(self.vars['context']['for-each'], dict):
                self.context_for_each = underscore_var_names(deepcopy(self.vars['context']['for-each']))

    def process(self, db):
        self.context.update(self.context_static)
        self.context.update(self.process_context_dynamic(db))
        return self.process_complex(db) if self.complex else self.process_simple(db)

    def process_complex(self, db):
        rendered_views = {}
        path_var_instances = db.query(self.path_query)
        logger.debug("Complex view %s generated %d possible path(s)" % (self.name, len(path_var_instances)))
        for inst in path_var_instances:
            # render the path template to get this instance's view path
            inst_path = self.reverse_url(inst=inst)
            inst_path_ext = get_url_file_ext(inst_path)
            # if the output path doesn't have an output file extension, we assume that we have to add one
            if inst_path_ext is None or len(inst_path_ext) == 0:
                inst_path = add_url_path_component(
                        inst_path,
                        '%s%s' % (self.default_output_filename, self.template_ext)
                )

            # update the context with the current path variable instance
            self.context[self.path_variable] = inst
            self.context.update(self.render_context_for_each(db, inst))
            # render the template itself
            rendered_view = self.template.render(**self.context)
            rendered_views = deep_merge_dict(
                    rendered_views,
                    dict_from_path(inst_path, final_value=rendered_view)
            )
        return rendered_views

    def render_context_for_each(self, db, inst):
        result = dict()
        for k, v in self.context_for_each.items():
            result[k] = db.query(v, additional_locals={self.path_variable: inst})
        return result

    def process_simple(self, db):
        inst_path_ext = get_url_file_ext(self.path)
        if inst_path_ext is None or len(inst_path_ext) == 0:
            path = add_url_path_component(self.path, '%s%s' % (self.default_output_filename, self.template_ext))
        else:
            path = self.path
        return dict_from_path(
                path,
                final_value=self.template.render(**self.context),
        )

    def process_context_dynamic(self, db):
        result = {}
        for var, query in self.context_dynamic.items():
            result[var] = db.query(query)
        return result

    def reverse_url(self, inst=None):
        """Returns the reverse lookup URL for this view."""
        result = self.template_env.from_string(
                self.path_template
        ).render(
                **{self.path_variable: inst}
        ) if self.complex else self.path

        return result if result.endswith('/') else ('%s/' % result)
