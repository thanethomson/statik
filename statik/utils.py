# -*- coding:utf-8 -*-
"""
Utility functions for Statik.
"""

import os
import os.path
import pprint
import json
import shutil
from slugify import slugify as _slugify

__all__ = [
    'get_abs_path',
    'pretty',
    'slugify',
    'load_json_file',
    'list_dir',
    'copy_tree',
]


def get_abs_path(path, rel_base_path=None):
    """Expands the specified path as far as possible to an absolute path.

    TODO: Handle Windows relative path expansion here properly.

    Args:
        path: The initial path (can be absolute or relative or relative to the
            user's home directory).
        rel_base_path: If the specified path is relative, it will be joined to
            this base path.

    Returns:
        The expanded path. If the specified path is already absolute, it returns
        the path unchanged.
    """
    if path.startswith('~'):
        return os.path.expanduser(path)
    elif not path.startswith('/'):
        return os.path.abspath(path if rel_base_path is None else \
            os.path.join(rel_base_path, path))
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


def load_json_file(filename):
    """Loads data from the specified JSON file.

    Args:
        filename: The absolute path of the file to read.

    Returns:
        A string containing a Python dictionary of the interpreted JSON from
        the contents of the specified file.
    """
    result = {}
    with open(filename, 'rt') as f:
        result = json.load(f)
    return result


def list_dir(path, exts):
    """Lists the contents of the specified path that have the specified
    file extensions. Not recursive.

    Args:
        path: The absolute path in which to look for files.
        exts: A list of file extensions against which to match.
    """
    result = []
    for filename in os.listdir(path):
        _, ext = os.path.splitext(filename)
        ext = ext.lstrip(".")
        if ext in exts:
            result.append(filename)
    return result


def copy_tree(src_path, dest_path, recursive=True):
    """Similar to the shutil.copytree() function, except that it doesn't
    throw exceptions when the destination path or files already exist.

    Args:
        src_path: The path to the source folder to copy.
        dest_path: The path to the destination folder, into which files
            will be copied.
        recursive: Whether or not the copy should be performed recursively.

    Returns:
        The number of files copied in this operation.
    """
    if not os.path.isdir(dest_path):
        # create the destination directory
        os.makedirs(dest_path)

    files_copied = 0

    # list the source directory's contents
    src_contents = os.listdir(src_path)
    for name in src_contents:
        full_src = os.path.join(src_path, name)
        full_dest = os.path.join(dest_path, name)
        if os.path.isdir(full_src):
            if recursive:
                files_copied += copy_tree(full_src, full_dest, recursive=True)
        else:
            # copy the file contents, overwriting it if it exists
            shutil.copyfile(full_src, full_dest)
            files_copied += 1

    return files_copied
