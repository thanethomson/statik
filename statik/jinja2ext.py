# -*- coding:utf-8 -*-

from jinja2 import nodes
from jinja2.ext import Extension

from statik.utils import add_url_path_component

__all__ = [
    'StatikUrlExtension',
    'StatikAssetExtension',
    'filter_datetime',
]


class StatikUrlExtension(Extension):
    """Provides the `{% url %}` extension for reverse-location of URLs from views/data."""

    tags = {'url'}

    def __init__(self, environment):
        super().__init__(environment)

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
        super().__init__(environment)

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


def filter_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    return value.strftime(format)
