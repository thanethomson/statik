# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from statik.templatetags import register
from slugify import slugify


@register.filter(name='slugify')
def filter_slugify(s):
    return slugify(s)

