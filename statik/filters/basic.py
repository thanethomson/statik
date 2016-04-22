# -*- coding:utf-8 -*-
"""
Basic Jinja2 filters for Statik.
"""

import dateutil.parser
from statik import utils

__all__ = [
    'date',
    'slug',
]


def date(dateval, fmt="%Y-%m-%d"):
    """Formats the specified date/datetime value using the given string
    formatting specifier (as per strftime).

    Args:
        dateval: A date or datetime object.
        fmt: An optional string formatting specifier, as per the
            strftime() function for date and datetime.

    Returns:
        A string containing the formatting date/datetime value.
    """
    if isinstance(dateval, basestring):
        # first convert it to a datetime object
        dateval = dateutil.parser.parse(dateval)
    return dateval.strftime(fmt) if dateval else ""


def slug(s):
    """Converts the specified string to its slugified value.

    For example, for an input string "Hello world!", the slugified value
    will be "hello-world".

    Args:
        s: The input string.

    Returns:
        A string containing the slugified version of the input string.
    """
    return utils.slugify(s) if s else ""
