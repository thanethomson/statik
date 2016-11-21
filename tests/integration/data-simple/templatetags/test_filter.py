# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from statik.templatetags import register


@register.filter(name="test_lower")
def filter_my_lowercase(s):
    return s.lower()
