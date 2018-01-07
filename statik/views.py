# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from future.utils import iteritems
from past.builtins import basestring

from copy import deepcopy, copy

from statik.common import YamlLoadable
from statik.errors import *
from statik.utils import *
from statik.context import StatikContext

import logging

logger = logging.getLogger(__name__)

__all__ = [
    'StatikView',
    'StatikViewPath',
    'StatikViewSimplePath',
    'StatikViewComplexPath',
    'StatikViewRenderer',
    'StatikSimpleViewRenderer',
    'StatikComplexViewRenderer'
]


class StatikViewPath(object):
    """Base class for encapsulation of the functionality relating to Statik views' paths."""

    def __init__(
            self,
            path,
            output_own_subfolder=True,
            output_filename='index',
            output_ext='.html',
            view_name=None,
            error_context=None,
        ):
        self.path = path
        self.output_own_subfolder = output_own_subfolder
        self.output_filename = output_filename
        self.output_ext = output_ext
        self.view_name = view_name
        self.error_context = error_context or StatikErrorContext()
        logger.debug(
            "Configured path for view \"%s\": %s",
            self.view_name,
            self
        )

    def render(self, inst=None, context=None):
        """Must render this path (optionally according to the given instance).
        
        Returns:
            A string containing the rendered path.
        """
        raise NotImplementedError()

    def render_reverse(self, inst=None, context=None):
        """Renders the reverse URL for this path."""
        rendered = self.render(inst=inst, context=context)
        parts = rendered.split('/')
        # we only prettify URLs for these files
        if parts[-1] in ['index.html', 'index.htm']:
            return ('/'.join(parts[:-1])) + '/'
        return rendered

    @classmethod
    def create(
            cls,
            path,
            template_engine=None,
            output_filename=None,
            output_ext=None,
            view_name=None
        ):
        """Create the relevant subclass of StatikView based on the given path variable and
        parameters."""
        # if it's a complex view
        if isinstance(path, dict):
            return StatikViewComplexPath(
                path,
                template_engine,
                output_filename=output_filename,
                output_ext=output_ext,
                view_name=view_name
            )
        elif isinstance(path, basestring):
            return StatikViewSimplePath(
                path,
                output_filename=output_filename,
                output_ext=output_ext,
                view_name=view_name
            )
        else:
            raise ValueError(
                "Unrecognised structure for \"path\" configuration in view: %s" % view_name
            )


class StatikViewSimplePath(StatikViewPath):
    """A simple path, whose output only renders to a single file."""

    def __init__(self, path, **kwargs):
        super(StatikViewSimplePath, self).__init__(path, **kwargs)
        output_ext = get_url_file_ext(self.path)
        # if an output extension's been supplied, we interpret it to mean that we won't
        # be creating our own output subfolder
        if output_ext:
            self.output_own_subfolder = False

        if self.output_own_subfolder:
            self.path = add_url_path_component(
                self.path,
                "%s%s" % (self.output_filename, self.output_ext)
            )

    def __repr__(self):
        return "StatikViewSimplePath(path=%s)" % self.path

    def __str__(self):
        return repr(self)

    def render(self, inst=None, context=None):
        return self.path


class StatikViewComplexPath(StatikViewPath):
    """A complex path, whose output renders to multiple files based on the model instance
    supplied."""

    def __init__(self, path, template_engine, **kwargs):
        error_context = kwargs.pop('error_context', StatikErrorContext())
        if not isinstance(path, dict):
            raise InvalidViewFieldTypeError(
                "path",
                "a dictionary/map",
                view_name=self.view_name,
                context=error_context
            )
        if 'template' not in path:
            raise MissingViewFieldError(
                "template",
                view_name=self.view_name,
                context=error_context
            )
        if 'for-each' not in path:
            raise MissingViewFieldError(
                "for-each",
                view_name=self.view_name,
                context=error_context
            )
        if not isinstance(path['for-each'], dict) or len(path['for-each']) != 1:
            raise InvalidViewFieldTypeError(
                "for-each",
                "a single key/value pair",
                view_name=self.view_name,
                context=self.error_context
            )
        self.raw_template = path['template']
        self.template = template_engine.create_template(self.raw_template)
        self.variable, self.query = list(iteritems(path['for-each']))[0]

        super(StatikViewComplexPath, self).__init__(
            path,
            error_context=error_context,
            **kwargs
        )

    def __repr__(self):
        return "StatikViewComplexPath(template=%s, variable=%s, query=%s)" % (
            self.template, self.variable, self.query
        )

    def __str__(self):
        return repr(self)

    def render(self, inst=None, context=None):
        if context is not None and not isinstance(context, dict):
            raise TypeError(
                "Path renderer requires a dict as context, but got %s" %
                context.__class__.__name__
            )
        ctx = copy(context) if context else dict()
        ctx[self.variable] = inst
        result = self.template.render(ctx)
        result_ext = get_url_file_ext(result)
        if not result_ext:
            result = add_url_path_component(
                result,
                "%s%s" % (self.output_filename, self.output_ext)
            )
        return result


class StatikViewRenderer(object):
    """Base class for the different kinds of Statik view renderers."""

    def __init__(self, path, template, view_name=None, error_context=None):
        self.path = path
        self.template = template
        self.view_name = view_name
        self.error_context = error_context or StatikErrorContext()
        logger.debug(
            "Configured Statik view renderer for view \"%s\": %s",
            view_name,
            self
        )

    def render(self, context, db=None, safe_mode=False, extra_context=None):
        raise NotImplementedError()

    @classmethod
    def create(cls, path, template, view_name=None):
        if isinstance(path, StatikViewSimplePath):
            return StatikSimpleViewRenderer(
                path, template, view_name=view_name
            )
        elif isinstance(path, StatikViewComplexPath):
            return StatikComplexViewRenderer(
                path, template, view_name=view_name
            )
        raise TypeError(
            "Unsupported path type %s for view %s" % (path.__class__.__name__, view_name)
        )


class StatikSimpleViewRenderer(StatikViewRenderer):
    """Renderer for simple Statik views (only a single output file)."""

    def __init__(self, path, template, view_name=None, error_context=None):
        if not isinstance(path, StatikViewSimplePath):
            raise TypeError(
                "Simple Statik view renderers only accept simple paths (in view %s)" % view_name
            )
        super(StatikSimpleViewRenderer, self).__init__(
            path,
            template,
            view_name=view_name,
            error_context=error_context
        )

    def __repr__(self):
        return "StatikSimpleViewRenderer(path=%s)" % self.path

    def __str__(self):
        return repr(self)

    def render(self, context, db=None, safe_mode=False, extra_context=None):
        ctx = context.build(db=db, safe_mode=safe_mode, extra=extra_context)
        logger.debug("Rendering view %s with context: %s", self.view_name, ctx)
        return dict_from_path(
            self.path.render(),
            final_value=self.template.render(ctx)
        )


class StatikComplexViewRenderer(StatikViewRenderer):
    """Renderer for complex Statik views (multiple output files from a single view, dependent on
    the results of a database query)."""

    def __init__(self, path, template, view_name=None, error_context=None):
        if not isinstance(path, StatikViewComplexPath):
            raise TypeError(
                "Complex Statik view renderers only accept complex paths (in view %s)" % view_name
            )
        super(StatikComplexViewRenderer, self).__init__(
            path,
            template,
            view_name=view_name,
            error_context=error_context
        )

    def __repr__(self):
        return "StatikComplexViewRenderer(path=%s)" % self.path

    def __str__(self):
        return repr(self)

    def render(self, context, db=None, safe_mode=False, extra_context=None):
        """Renders the given context using the specified database, returning a dictionary
        containing path segments and rendered view contents."""
        if not db:
            raise MissingParameterError(
                "db",
                context=self.error_context
            )
        rendered_views = dict()
        path_instances = db.query(self.path.query, safe_mode=safe_mode)
        extra_ctx = copy(extra_context) if extra_context else dict()

        for inst in path_instances:
            extra_ctx.update({
                self.path.variable: inst
            })
            ctx = context.build(
                db=db,
                safe_mode=safe_mode,
                for_each_inst=inst,
                extra=extra_ctx
            )
            inst_path = self.path.render(inst=inst, context=ctx)
            rendered_view = self.template.render(ctx)
            rendered_views = deep_merge_dict(
                rendered_views,
                dict_from_path(inst_path, final_value=rendered_view)
            )
        return rendered_views


class StatikView(YamlLoadable):
    """Our primary view interface, which renders data using templates."""

    def __init__(
            self,
            name=None,
            models=None,
            template_engine=None,
            template=None,
            initial_context=None,
            default_output_ext='.html',
            default_output_filename='index',
            **kwargs):
        super(StatikView, self).__init__(**kwargs)

        # defaults
        self.name = name or (
            extract_filename(self.filename) if self.filename else None
        )
        if not self.name:
            raise MissingParameterError("name", context=self.error_context)
        if 'path' not in self.vars or not self.vars['path']:
            raise MissingParameterError("path", context=self.error_context)
        self.path = StatikViewPath.create(
            self.vars['path'],
            template_engine=template_engine,
            output_filename=default_output_filename,
            output_ext=default_output_ext,
            view_name=self.name
        )
        pre_context = self.vars.get('context', dict())
        self.context = StatikContext(
            initial=initial_context,
            static=pre_context.get('static', None),
            dynamic=pre_context.get('dynamic', None),
            for_each=pre_context.get('for-each', None)
        )

        if models is None:
            raise MissingParameterError("models", context=self.error_context)
        # keep a reference to the models
        self.models = models

        # if no template was explicitly supplied, we need a template engine with which to
        # load templates
        self.template_engine = template_engine
        if not template:
            if not template_engine:
                raise MissingParameterError(
                    "template_engine", "template",
                    context=self.error_context
                )
            if 'template' not in self.vars:
                raise MissingParameterError(
                    "template",
                    context=self.error_context
                )
            self.template = template_engine.load_template(
                self.vars['template']
            )

        self.renderer = StatikViewRenderer.create(
            self.path,
            self.template,
            view_name=self.name
        )

        logger.debug('%s', self)

    def __repr__(self):
        return "StatikView(name=%s, path=%s, template=%s, renderer=%s)" % (
            self.name, self.path, self.template, self.renderer
        )

    def __str__(self):
        return repr(self)

    def process(self, db, safe_mode=False, extra_context=None):
        """Deprecated. Rather use StatikView.render()."""
        return self.renderer.render(
            self.context,
            db,
            safe_mode=safe_mode,
            extra_context=extra_context
        )

    def render(self, db, safe_mode=False, extra_context=None):
        """Renders this view, given the specified StatikDatabase instance."""
        return self.renderer.render(
            self.context,
            db,
            safe_mode=safe_mode,
            extra_context=extra_context
        )

    def reverse_url(self, inst=None):
        """Returns the reverse lookup URL for this view."""
        return self.path.render_reverse(inst=inst)
