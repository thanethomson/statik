# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from io import open
import os.path

import jinja2
import pystache

from statik.errors import *
from statik.utils import *
from statik import templatetags

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'StatikTemplateEngine',
    'StatikTemplate',
    'StatikTemplateProvider',
    'StatikJinjaTemplate',
    'StatikJinjaTemplateProvider',
    'StatikMustacheTemplateProvider',
    'StatikMustacheTemplate',
    'DEFAULT_TEMPLATE_PROVIDERS',
    'SAFER_TEMPLATE_PROVIDERS'
]

# our default template engine providers, in order of precedence
DEFAULT_TEMPLATE_PROVIDERS = [
    "jinja2",
    "mustache"
]
# template providers that we consider to be "safe"
SAFER_TEMPLATE_PROVIDERS = [
    "mustache"
]
TEMPLATE_PROVIDER_EXTS = {
    "jinja2": [".html.jinja2", ".jinja2", ".html"],
    "mustache": [".html.mustache", ".mustache", ".html"]
}


def get_template_provider_class(provider):
    provider_classes = {
        "jinja2": StatikJinjaTemplateProvider,
        "mustache": StatikMustacheTemplateProvider
    }
    return provider_classes[provider]


def template_exception_handler(fn, error_context, filename=None):
    """Calls the given function, attempting to catch any template-related errors, and
    converts the error to a Statik TemplateError instance. Returns the result returned
    by the function itself."""
    error_message = None
    if filename:
        error_context.update(filename=filename)
    try:
        return fn()
    except jinja2.TemplateSyntaxError as exc:
        error_context.update(filename=exc.filename, line_no=exc.lineno)
        error_message = exc.message
    except jinja2.TemplateError as exc:
        error_message = exc.message
    except Exception as exc:
        error_message = "%s" % exc

    raise TemplateError(message=error_message, context=error_context)        


class StatikTemplateEngine(object):
    """Provides a common interface to different underlying template engines. At present,
    Jinja2 and Mustache templates are supported."""

    def __init__(self, project, error_context=None):
        """Constructor.

        Args:
            project: The project to which this template engine relates.
        """
        self.project = project
        self.error_context = error_context or StatikErrorContext()
        self.supported_providers = project.config.template_providers
        if project.safe_mode:
            self.supported_providers = [provider for provider in self.supported_providers \
                                        if provider in SAFER_TEMPLATE_PROVIDERS]

        if len(self.supported_providers) == 0:
            raise NoSupportedTemplateProvidersError(
                SAFER_TEMPLATE_PROVIDERS if project.safe_mode else DEFAULT_TEMPLATE_PROVIDERS,
                project.safe_mode
            )

        self.provider_classes = dict()
        self.providers_by_ext = dict()
        self.exts = []
        for provider in self.supported_providers:
            self.provider_classes[provider] = get_template_provider_class(provider)
            # track which provider to use for which file extension
            for ext in TEMPLATE_PROVIDER_EXTS[provider]:
                if ext not in self.providers_by_ext:
                    self.providers_by_ext[ext] = provider
                    self.exts.append(ext)

        self.providers = dict()
        self.cached_templates = dict()

        # build up our expected template paths
        # we allow the templates/ folder to take highest precedence
        self.template_paths = [os.path.join(project.path, project.TEMPLATES_DIR)]
        # if this project has a theme associated with it
        if project.config.theme is not None:
            self.template_paths.append(os.path.join(
                project.path,
                project.THEMES_DIR,
                project.config.theme,
                project.TEMPLATES_DIR
            ))

        logger.debug(
            "Looking in the following path(s) (in the following order) for templates:\n%s",
            "\n".join(self.template_paths)
        )

        # now make sure that all of the relevant template paths actually exist
        for path in self.template_paths:
            if not os.path.exists(path) or not os.path.isdir(path):
                raise MissingProjectFolderError(path)

        logger.debug(
            "Configured the following template providers: %s",
            ", ".join(self.supported_providers)
        )

    def get_provider(self, name):
        """Allows for lazy instantiation of providers (Jinja2 templating is heavy, so only instantiate it if
        necessary)."""
        if name not in self.providers:
            cls = self.provider_classes[name]
            # instantiate the provider
            self.providers[name] = cls(self)
        return self.providers[name]

    def find_template_details(self, name):
        base_path = None
        name_with_ext = name
        found_ext = None
        for ext in self.exts:
            if name.endswith(ext):
                found_ext = ext

        if found_ext is None:
            base_path, found_ext = find_first_file_with_ext(self.template_paths, name, self.exts)
            if base_path is None or found_ext is None:
                raise MissingTemplateError(name=name)
            name_with_ext = "%s%s" % (name, found_ext)

        return name_with_ext, self.providers_by_ext[found_ext], base_path

    def load_template(self, name):
        """Attempts to load the relevant template from our templating system/environment.

        Args:
            name: The name of the template to load.

        Return:
            On success, a StatikTemplate object that can be used to render content.
        """
        # hopefully speeds up loading of templates a little, especially when loaded multiple times
        if name in self.cached_templates:
            logger.debug("Using cached template: %s", name)
            return self.cached_templates[name]

        logger.debug("Attempting to find template by name: %s", name)
        name_with_ext, provider_name, base_path = self.find_template_details(name)

        full_path = None
        if base_path is not None:
            full_path = os.path.join(base_path, name_with_ext)

        # load it with the relevant provider
        template = template_exception_handler(
            lambda: self.get_provider(provider_name).load_template(
                name_with_ext,
                full_path=full_path
            ),
            self.error_context,
            filename=full_path
        )

        # cache it for potential later use
        self.cached_templates[name] = template
        return template

    def create_template(self, s, provider_name=None):
        """Creates a template from the given string based on the specified provider or the provider with
        highest precedence.

        Args:
            s: The string to convert to a template.
            provider_name: The name of the provider to use to create the template.
        """
        if provider_name is None:
            provider_name = self.supported_providers[0]
        return template_exception_handler(
            lambda: self.get_provider(provider_name).create_template(s),
            self.error_context
        )


class StatikTemplate(object):
    """Abstract class to act as an interface to the underlying templating engine's templates."""

    def __init__(self, filename, error_context=None):
        self.filename = filename
        self.error_context = error_context or StatikErrorContext()

    def render(self, context):
        return template_exception_handler(
            lambda: self.do_render(context),
            self.error_context,
            filename=self.filename
        )

    def do_render(self, context):
        """Renders this template using the given context data."""
        raise NotImplementedError("Must be implemented in subclasses")


class StatikTemplateProvider(object):
    """Abstract base class for all template providers."""

    def __init__(self, engine, error_context=None):
        """Constructor."""
        if not isinstance(engine, StatikTemplateEngine):
            raise TypeError(
                "Expecting a StatikTemplateEngine instance to initialise template provider"
            )
        self.engine = engine
        self.error_context = error_context or StatikErrorContext()

    def load_template(self, name, full_path=None):
        """Loads the template with the given name/filename."""
        raise NotImplementedError("Must be implemented in subclasses")

    def create_template(self, s):
        """Creates a template from the given string."""
        raise NotImplementedError("Must be implemented in subclasses")


class StatikJinjaTemplateProvider(StatikTemplateProvider):
    """Template provider specifically for Jinja2."""

    expected_template_exts = TEMPLATE_PROVIDER_EXTS["jinja2"]

    def __init__(self, engine):
        """Constructor.

        Args:
            engine: The StatikTemplateEngine to which this template provider belongs.
        """
        super(StatikJinjaTemplateProvider, self).__init__(engine)
        project = engine.project

        logger.debug("Instantiating Jinja2 template provider")

        # now load our template tags
        self.templatetags_path = os.path.join(project.path, project.TEMPLATETAGS_DIR)
        if os.path.exists(self.templatetags_path) and os.path.isdir(self.templatetags_path):
            # dynamically import modules; they register themselves with our template tag store
            import_python_modules_by_path(self.templatetags_path)

        extensions = [
            'statik.jinja2ext.StatikUrlExtension',
            'statik.jinja2ext.StatikAssetExtension',
            'statik.jinja2ext.StatikLoremIpsumExtension',
            'statik.jinja2ext.StatikTemplateTagsExtension',
            'jinja2.ext.do',
            'jinja2.ext.loopcontrols',
            'jinja2.ext.with_',
            'jinja2.ext.autoescape',
        ]

        jinja2_config = project.config.vars.get('jinja2', dict())
        extensions.extend(jinja2_config.get('extensions', list()))

        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                engine.template_paths,
                encoding=project.config.encoding
            ),
            extensions=extensions
        )

        if templatetags.store.filters:
            logger.debug(
                "Loaded custom template tag filters: %s",
                ", ".join(templatetags.store.filters)
            )
            self.env.filters.update(templatetags.store.filters)

        # configure views for the Jinja2 templating environment
        self.env.statik_views = project.views
        self.env.statik_base_url = project.config.base_path
        self.env.statik_base_asset_url = add_url_path_component(
            project.config.base_path,
            project.config.assets_dest_path
        )

    def reattach_project_views(self):
        if len(self.env.statik_views) == 0:
            self.env.statik_views = self.engine.project.views

    def load_template(self, name, full_path=None):
        logger.debug("Attempting to load Jinja2 template: %s", name)
        return StatikJinjaTemplate(self, self.env.get_template(name))

    def create_template(self, s):
        return StatikJinjaTemplate(self, self.env.from_string(s))


class StatikJinjaTemplate(StatikTemplate):
    """Wraps a simple Jinja2 template."""

    def __init__(self, provider, template, **kwargs):
        """Constructor.

        Args:
            provider: The provider that created this template.
            template: The Jinja2 template to wrap.
        """
        super(StatikJinjaTemplate, self).__init__(template.filename, **kwargs)
        self.provider = provider
        self.template = template

    def __repr__(self):
        return "StatikJinjaTemplate(template=%s)" % self.template

    def __str__(self):
        return repr(self)

    def do_render(self, context):
        # make sure we lazily reattach our provider's environment to the project's views
        self.provider.reattach_project_views()
        return self.template.render(**context)


class StatikMustachePartialGetter(object):

    def __init__(self, provider):
        self.provider = provider
        self.cache = dict()

    def get(self, partial_name):
        if partial_name in self.cache:
            return self.cache[partial_name]

        logger.debug("Attempting to load Mustache partial: %s", partial_name)
        content = self.provider.load_template_content(partial_name)
        self.cache[partial_name] = content
        return content


class StatikMustacheTemplateProvider(StatikTemplateProvider):
    """Template provider specifically for Mustache templates."""

    expected_template_exts = TEMPLATE_PROVIDER_EXTS["mustache"]

    def __init__(self, engine, **kwargs):
        super(StatikMustacheTemplateProvider, self).__init__(engine, **kwargs)
        logger.debug("Instantiating Mustache template provider")
        self.renderer = pystache.Renderer(partials=StatikMustachePartialGetter(self))

    def load_template_content(self, name, full_path=None):
        logger.debug("Attempting to load Mustache template: %s", name)
        if full_path is None:
            base_path, ext = find_first_file_with_ext(
                self.engine.template_paths,
                name,
                self.expected_template_exts
            )
            if base_path is None or ext is None:
                raise MissingTemplateError(
                    name=name,
                    kind="Mustache",
                    context=self.error_context
                )
            full_path = os.path.join(base_path, "%s%s" % (name, ext))

        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise MissingTemplateError(
                path=full_path,
                kind="Mustache",
                context=self.error_context
            )

        # read the template's content from the file
        with open(full_path, encoding=self.engine.project.config.encoding) as f:
            template_content = f.read()

        return template_content

    def load_template(self, name, full_path=None):
        return self.create_template(
            self.load_template_content(name, full_path=full_path),
            filename=full_path
        )

    def create_template(self, s, filename=None):
        return StatikMustacheTemplate(
            pystache.parse(_unicode(s)),
            self.renderer,
            filename=filename
        )


class StatikMustacheTemplate(StatikTemplate):
    """Wraps a simple Mustache template."""

    def __init__(self, parsed_template, renderer, filename=None, error_context=None):
        super(StatikMustacheTemplate, self).__init__(
            filename,
            error_context=error_context
        )
        self.parsed_template = parsed_template
        self.renderer = renderer

    def __repr__(self):
        return "StatikMustacheTemplate(parsed_template=%s)" % self.parsed_template

    def __str__(self):
        return repr(self)

    def do_render(self, context):
        return self.renderer.render(self.parsed_template, context)
