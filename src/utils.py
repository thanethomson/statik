# -*- coding:utf-8 -*-
"""
Utility functions for Statik.
"""

import os.path
import pprint
from slugify import slugify as _slugify

__all__ = [
    'get_abs_path',
    'pretty',
    'slugify',
    'list_dir',
]


def get_abs_path(path):
    """Expands the specified path as far as possible to an absolute path.

    TODO: Handle Windows relative path expansion here properly.

    Args:
        path: The initial path (can be absolute or relative or relative to the
            user's home directory).

    Returns:
        The expanded path. If the specified path is already absolute, it returns
        the path unchanged.
    """
    if path.startswith('~'):
        return os.path.expanduser(path)
    elif not path.startswith('/'):
        return os.path.abspath(path)
    # unchanged
    return path


def pretty(obj):
    """Wrapper for converting the specified object into a pretty-printed
    string representation.

    Args:
        obj: An object to pretty print to string.

    Returns:
        A string containing the pretty-printed object.
    """
    return pprint.pformat(obj, indent=2)


def slugify(s):
    """Returns the slugified version of the specified string.

    For example, for an input string "Hello world", this will return the
    output string "hello-world".

    Args:
        s: The input string.

    Returns:
        A string containing the slugified version of the input string.
    """
    return _slugify(s)


def list_dir(path, exts):
    """Lists the contents of the specified path that have the specified
    file extensions. Not recursive.

    Args:
        path: The absolute path in which to look for files.
        exts: A list of file extensions against which to match.
    """
    result = []
    for filename in os.path.listdir(path):
        _, ext = os.path.split(filename)
        ext = ext.lstrip(".")
        if ext in exts:
            result.append(ext)
    return result
