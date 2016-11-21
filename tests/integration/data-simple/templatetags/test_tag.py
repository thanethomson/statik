# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from statik.templatetags import register


@register.simple_tag(name='hello_world')
def hello_world_tag(*args, **kwargs):
    return "Hello world!"
