# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from statik.templatetags import register


@register.filter(name="date")
def filter_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    return value.strftime(format)


@register.filter(name="sort_by")
def filter_sort_by(lst, key):
    reverse = False
    if key.startswith('-'):
        reverse = True
        key = key.lstrip('-')
    return sorted(lst, key=lambda x: getattr(x, key), reverse=reverse)
