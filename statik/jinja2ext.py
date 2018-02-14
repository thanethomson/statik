# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.exceptions import TemplateSyntaxError

from statik.utils import add_url_path_component
from statik import templatetags

import lipsum

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'StatikUrlExtension',
    'StatikAssetExtension',
    'StatikTemplateTagsExtension',
    'StatikLoremIpsumExtension'
]


class StatikUrlExtension(Extension):
    """Provides the `{% url %}` extension for reverse-location of URLs from views/data."""

    tags = {'url'}

    def __init__(self, environment):
        super(StatikUrlExtension, self).__init__(environment)

        environment.extend(
            statik_views={},
            statik_base_url=''
        )

    def _url(self, view_name, inst):
        views = self.environment.statik_views
        if view_name not in views:
            raise KeyError("Unrecognised view: \"%s\"" % view_name)
        return add_url_path_component(
            self.environment.statik_base_url,
            views[view_name].reverse_url(inst)
        )

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        # get the first parameter: the view name
        args = [parser.parse_expression()]

        # if there's a comma, we've also got an instance variable here
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            # no instance supplied for URL tag
            args.append(nodes.Const(None))

        return nodes.Output(
            [self.call_method('_url', args)],
            lineno=lineno
        )


class StatikAssetExtension(Extension):
    """Provides the `{% asset %}` extension for embedding URLs to asset files in your templates."""

    tags = {'asset'}

    def __init__(self, environment):
        super(StatikAssetExtension, self).__init__(environment)

        environment.extend(
            statik_base_asset_url=''
        )

    def _asset(self, filename):
        return add_url_path_component(
            self.environment.statik_base_asset_url,
            filename
        )

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        # get the first parameter: the relative URL of the asset file
        args = [parser.parse_expression()]

        return nodes.Output(
            [self.call_method('_asset', args)],
            lineno=lineno
        )


class StatikLoremIpsumExtension(Extension):
    """Allows users to generate "Lorem Ipsum" text/filler for their templates. This extension only supports
    generating words and sentences. It can generate a single paragraph of Lorem Ipsum text if no parameters
    are supplied."""

    tags = {"lipsum"}
    GENERATORS = {
        "words": lipsum.generate_words,
        "sentences": lipsum.generate_sentences,
        "paragraphs": lipsum.generate_paragraphs
    }

    def _lipsum(self, count, kind):
        return self.GENERATORS[kind](int(count))

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        next_token = parser.stream.look()
        # if there are parameters
        if next_token.type == "comma":
            args = [parser.parse_expression()]
            if parser.stream.skip_if('comma'):
                args.append(parser.parse_expression())
            else:
                raise TemplateSyntaxError("Missing Lorem Ipsum generator parameter: kind", lineno)

            if args[1].value not in self.GENERATORS:
                raise TemplateSyntaxError(
                    "Supported Lorem Ipsum generator kinds are: %s" % ", ".join(self.GENERATORS.keys()),
                    lineno
                )
        else:
            # if no parameters were supplied
            args = [nodes.Const(1), nodes.Const("paragraphs")]

        return nodes.Output(
            [self.call_method("_lipsum", args)],
            lineno=lineno
        )


class StatikTemplateTagsExtension(Extension):

    @property
    def tags(self):
        return set(templatetags.store.tags.keys())

    def __init__(self, environment):
        super(StatikTemplateTagsExtension, self).__init__(environment)
        self.active_tag = None
        logger.debug("Loaded custom template tags: %s", ", ".join(self.tags))

    def _invoke_tag(self, tag_name, context, *args, **kwargs):
        return templatetags.store.invoke_tag(tag_name, context, *args, **kwargs)

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        # get the context
        context = nodes.ContextReference()

        # get the arguments
        args = [context]
        try:
            while True:
                args.append(parser.parse_expression())
        except TemplateSyntaxError:
            pass  # no more arguments

        # get the tag_name for use in looking up callable
        self.active_tag = parser._tag_stack[-1]
        args.insert(0, nodes.Const(self.active_tag))

        # create the node
        node = self.call_method('_invoke_tag', args=args, lineno=lineno)

        return nodes.Output(
            [node],
            lineno=lineno
        )
