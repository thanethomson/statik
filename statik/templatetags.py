# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from builtins import dict

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'TemplateTagStore',
    'register',
]


class TemplateTagStore(object):
    """
        To register a template tag:
            from statik.templatetags import register

            @register.filter
            def my_filter(object, argument):
                return object / argument
    """

    def __init__(self):
        self.filters = dict()
        self.tags = dict()
        self.takes_context = dict()

    def invoke_tag(self, tag_name, context, *args, **kwargs):
        if self.takes_context[tag_name]:
            return self.tags[tag_name](context, *args, **kwargs)
        return self.tags[tag_name](*args, **kwargs)

    def register_tag(self, name, fn):
        self.tags[name] = fn

    def register_filter(self, name, fn):
        self.filters[name] = fn

    def simple_tag(self, *args, **kwargs):
        _self = self
        name = kwargs.pop('name', None)
        if name is not None:
            def decorator(fn):
                logger.debug("Registering tag: %s", name)
                _self.register_tag(name, fn)
            ret = decorator
        else:
            fn = args[0]
            name = getattr(fn, '_decorated_function', fn).__name__
            logger.debug("Registering tag: %s", name)
            self.register_tag(name, fn)
            ret = None

        # do we need to pass context to tag callable?
        self.takes_context[name] = kwargs.pop('takes_context', False)

        return ret

    def filter(self, *args, **kwargs):
        _self = self
        name = kwargs.pop('name', None)
        if name is not None:
            def decorator(fn):
                logger.debug("Registering filter: %s", name)
                _self.register_filter(name, fn)
            ret = decorator
        else:
            fn = args[0]
            name = getattr(fn, '_decorated_function', fn).__name__
            logger.debug("Registering filter: %s", name)
            self.register_filter(name, fn)
            ret = None

        # do we need to pass context to filter callable?
        self.takes_context[name] = kwargs.pop('takes_context', False)

        return ret


store = TemplateTagStore()
register = store  # for clarity when using decorators
