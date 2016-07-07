# -*- coding:utf-8 -*-

from statik.templatetags import register


@register.simple_tag(name="context", takes_context=True)
def print_context(context, *args):
    return context


@register.simple_tag(name="ditto")
def echo_arguments(*args, **kwargs):
    """ Echoes all parameters back as text (for debugging)
            {% ditto 1 2 3 %} => "ditto(1, 2, 3)"
    """
    args_string = ', '.join(map(lambda x: str(x), args))
    kwargs_string = ', '.join(map(lambda k, v: "%s=%s" % (k, v), kwargs.items()))
    string_lst = filter(lambda x: bool(x), [args_string, kwargs_string])
    return "ditto(%s)" % ", ".join(string_lst)
