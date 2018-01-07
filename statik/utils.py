# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from future.utils import iteritems
from io import open

import os
import os.path
import stat
from copy import deepcopy, copy
import shutil

import six

if six.PY3:
    import importlib.util
elif six.PY2:
    import imp

from glob import glob

import logging
logger = logging.getLogger(__name__)


__all__ = [
    'list_files',
    'extract_filename',
    'dict_from_path',
    'deep_merge_dict',
    'underscore_var_names',
    'add_url_path_component',
    'copy_tree',
    'calculate_association_table_name',
    'get_url_file_ext',
    'generate_quickstart',
    'import_python_modules_by_path',
    'get_project_config_file',
    'dict_strip',
    'strip_str',
    'strip_el_text',
    '_str',
    '_unicode',
    'find_first_file_with_ext',
    'uncapitalize'
]

DEFAULT_CONFIG_CONTENT = """project-name: Your project name
base-path: /
"""


def list_files(base_path, ext=None):
    """Lists all of the files in the given base directory, optionally only
    including whose extension(s) match the ext string/list of strings.
    This is non-recursive.

    Args:
        base_path: The directory in which to search.
        ext: The extension(s) to match in the given directory. If None, this
            matches all file extensions.

    Returns:
        A list of filenames relative to the given base path.
    """
    if not os.path.isdir(base_path):
        raise ValueError("Path does not exist: %s" % base_path)

    files = []
    for entry in os.listdir(base_path):
        if os.path.isfile(os.path.join(base_path, entry)):
            _, entry_ext = os.path.splitext(entry)
            entry_ext = entry_ext.lstrip('.')

            if (ext is None) or \
                (isinstance(ext, str) and entry_ext == ext) or \
                (isinstance(ext, list) and entry_ext in ext):
                files.append(entry)

    return files


def extract_filename(path):
    return list(os.path.splitext(os.path.basename(path)))[0]


def dict_from_path(path, final_value=dict()):
    components = path.split('/')
    last_dict = deepcopy(final_value)
    cur_dict = {}
    for i in range(-1, -len(components)-1, -1):
        if len(components[i]) > 0:
            cur_dict = {components[i]: last_dict}
            last_dict = deepcopy(cur_dict)

    return cur_dict


def deep_merge_dict(a, b):
    """Deep merges dictionary b into dictionary a."""
    if not isinstance(a, dict):
        raise TypeError("a must be a dict, but found %s" % a.__class__.__name__)
    if not isinstance(b, dict):
        raise TypeError("b must be a dict, but found %s" % b.__class__.__name__)

    _a = copy(a)
    _b = copy(b)

    for key_b, val_b in iteritems(_b):
        # if it's a sub-dictionary
        if isinstance(val_b, dict):
            if key_b not in _a or not isinstance(_a[key_b], dict):
                _a[key_b] = {}

            # perform the deep merge recursively
            _a[key_b] = deep_merge_dict(_a[key_b], val_b)
        else:
            _a[key_b] = val_b

    # b should now be deep-merged into a
    return _a


def underscore_var_names(d):
    _d = {}
    for k, v in iteritems(d):
        _k = k.replace('-', '_')
        # perform the underscoring recursively
        _d[_k] = underscore_var_names(v) if isinstance(v, dict) else v

    return _d


def add_url_path_component(path, component):
    return '%s/%s' % (path.rstrip('/'), component.lstrip('/'))


def copy_file_if_modified(src_path, dest_path):
    """Only copies the file from the source path to the destination path if it doesn't exist yet or it has
    been modified. Intended to provide something of an optimisation when a project has large trees of assets."""

    # if the destination path is a directory, delete it completely - we assume here we are
    # writing a file to the filesystem
    if os.path.isdir(dest_path):
        shutil.rmtree(dest_path)

    must_copy = False
    if not os.path.exists(dest_path):
        must_copy = True
    else:
        src_stat = os.stat(src_path)
        dest_stat = os.stat(dest_path)

        # if the size or last modified timestamp are different
        if ((src_stat[stat.ST_SIZE] != dest_stat[stat.ST_SIZE]) or
                (src_stat[stat.ST_MTIME] != dest_stat[stat.ST_MTIME])):
            must_copy = True

    if must_copy:
        shutil.copy2(src_path, dest_path)


def copy_tree(src_path, dest_path):
    """Copies the entire folder tree, recursively, from the given source path
    to the given destination path. If the destination path does not exist, it
    will be created. If it does, any files/folders within it will be
    overwritten, but none will be deleted."""
    files_copied = 0
    if os.path.isdir(src_path):
        # if the destination folder doesn't exist, create it
        if not os.path.isdir(dest_path):
            os.makedirs(dest_path)

        for entry in os.listdir(src_path):
            src_entry_path = os.path.join(src_path, entry)
            dest_entry_path = os.path.join(dest_path, entry)
            # if it's a sub-folder
            if os.path.isdir(src_entry_path):
                # copy its contents recursively
                files_copied += copy_tree(src_entry_path, dest_entry_path)
            else:
                copy_file_if_modified(src_entry_path, dest_entry_path)
                files_copied += 1

    return files_copied


def calculate_association_table_name(model1_name, model2_name):
    return '%s%s' % (tuple(sorted([model1_name, model2_name])))


def get_url_file_ext(url):
    """Attempts to extract the file extension from the given URL."""
    # get the last part of the path component
    filename = url.split('/')[-1]
    name, ext = os.path.splitext(filename)

    # handle case of files with leading dot
    if not ext and name and name[0] == '.':
        ext = name

    return ext


def generate_quickstart(project_path):
    """Generates all of the basic paths for a Statik project within the given project path. If the project path
     doesn't exist, it will be created."""
    ensure_path_exists(project_path)
    ensure_file_exists(os.path.join(project_path, "config.yml"), DEFAULT_CONFIG_CONTENT)
    ensure_path_exists(os.path.join(project_path, 'models'))
    ensure_path_exists(os.path.join(project_path, 'data'))
    ensure_path_exists(os.path.join(project_path, 'themes'))
    ensure_path_exists(os.path.join(project_path, 'templates'))
    ensure_path_exists(os.path.join(project_path, 'templatetags'))
    ensure_path_exists(os.path.join(project_path, 'views'))
    ensure_path_exists(os.path.join(project_path, 'assets'))


def ensure_path_exists(path):
    if not os.path.isdir(path):
        logger.info('Creating path: %s', path)
        os.makedirs(path)


def ensure_file_exists(path, default_content):
    if not os.path.isfile(path):
        logger.info('Creating file: %s' % path)
        with open(path, 'wt') as f:
            f.write(default_content)


def import_module(module_name, path):
    if six.PY3:
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    elif six.PY2:
        imp.load_source(module_name, path)


def import_python_modules_by_path(path):
    module_files = glob(os.path.join(path, "*.py"))
    for filename in module_files:
        name = extract_filename(filename)
        import_module(name, filename)


def _str(s):
    return s.encode("utf-8") if six.PY2 else s


def _unicode(s):
    return s.decode("utf-8") if six.PY2 and isinstance(s, str) else s


def get_project_config_file(path, default_config_file_name):
    """Attempts to extract the project config file's absolute path from the given path. If the path is a
    directory, it automatically assumes a "config.yml" file will be in that directory. If the path is to
    a .yml file, it assumes that that is the root configuration file for the project."""
    _path, _config_file_path = None, None
    path = os.path.abspath(path)

    if os.path.isdir(path):
        _path = path
        # use the default config file
        _config_file_path = os.path.join(_path, default_config_file_name)
        logger.debug("Using default project configuration file path: %s", _config_file_path)
    elif path.endswith(".yml"):
        _path = os.path.dirname(path)
        _config_file_path = path
        logger.debug("Using custom project configuration file path: %s", _config_file_path)

    return _path, _config_file_path


def dict_strip(d):
    """Strips whitespace from the string values of the given dictionary (recursively).

    Args:
        d: A dictionary object.

    Returns:
        A new dictionary object, whose string values' whitespace has been stripped out.
    """
    _d = deepcopy(d)
    for k, v in iteritems(d):
        if isinstance(v, str):
            _d[k] = v.strip()
        elif isinstance(v, dict):
            _d[k] = dict_strip(v)

    return _d


def strip_str(s):
    """Strips newlines and whitespace from the given string."""
    return ' '.join([w.strip() for w in s.strip().split('\n')])


def strip_el_text(el, max_depth=0, cur_depth=0):
    """Recursively strips the plain text out of the given XML etree element up to the desired depth.

    Args:
        el: The etree element to scan.
        max_depth: The depth to which to recursively strip text (default: 0).
        cur_depth: The current recursive depth to which we've scanned so far.

    Returns:
        The stripped, plain text from within the element.
    """
    # text in front of any child elements
    el_text = strip_str(el.text if el.text is not None else "")

    if cur_depth < max_depth:
        for child in el:
            el_text += " "+strip_el_text(child, max_depth=max_depth, cur_depth=cur_depth+1)
    else:
        # add the last child's tail text, if any
        children = list(el)
        if children is not None and len(children) > 0:
            if children[-1].tail is not None:
                el_text += " "+strip_str(children[-1].tail)

    # we skip the root element
    if cur_depth > 0:
        # in case there's any text at the end of the element
        if el.tail is not None:
            el_text += " "+strip_str(el.tail)

    return strip_str(el_text)


def find_first_file_with_ext(base_paths, prefix, exts):
    """Runs through the given list of file extensions and returns the first file with the given base
    path and extension combination that actually exists.

    Args:
        base_paths: The base paths in which to search for files.
        prefix: The filename prefix of the file for which to search.
        exts: An ordered list of file extensions for which to search.

    Returns:
        On success, a 2-tuple containing the base path in which the file was found, and the extension of the file.
        On failure, returns (None, None).
    """
    for base_path in base_paths:
        for ext in exts:
            filename = os.path.join(base_path, "%s%s" % (prefix, ext))
            if os.path.exists(filename) and os.path.isfile(filename):
                logger.debug("Found first file with relevant extension: %s", filename)
                return base_path, ext

    logger.debug("No files found for prefix %s, extensions %s", prefix, ", ".join(exts))
    return None, None


def uncapitalize(s):
    """If the given string begins with a capital letter, it converts it to lowercase."""
    return (s[:1].lower() + s[1:]) if s else ""
