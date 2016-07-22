# -*- coding:utf-8 -*-

from statik.templatetags import register
from slugify import slugify


@register.filter(name='slugify')
def filter_slugify(s):
    return slugify(s)

