# -*- coding:utf-8 -*-

from statik.templatetags import register
import random


@register.simple_tag(name='rand')
def tag_random(*args):
    lower_bound = 1
    upper_bound = 100
    if len(args) == 2:
        lower_bound = args[0]
        upper_bound = args[1]
    return random.randint(lower_bound, upper_bound)
