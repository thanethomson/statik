# -*- coding:utf-8 -*-

import os
import os.path
from copy import deepcopy, copy
import shutil

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
    'generate_quickstart'
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


def dict_from_path(path, final_value={}):
    components = path.split('/')
    last_dict = final_value
    cur_dict = {}
    for i in range(-1, -len(components)-1, -1):
        if len(components[i]) > 0:
            cur_dict = {components[i]: last_dict}
            last_dict = deepcopy(cur_dict)

    return cur_dict


def deep_merge_dict(a, b):
    """Deep merges dictionary b into dictionary a."""
    _a = copy(a)
    _b = copy(b)

    for key_b, val_b in _b.items():
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
    for k, v in d.items():
        _k = k.replace('-', '_')
        # perform the underscoring recursively
        _d[_k] = underscore_var_names(v) if isinstance(v, dict) else v

    return _d


def add_url_path_component(path, component):
    return '%s/%s' % (path.rstrip('/'), component.lstrip('/'))


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
                shutil.copy2(src_entry_path, dest_entry_path)
                files_copied += 1

    return files_copied


def calculate_association_table_name(model1_name, model2_name):
    return '%s%s' % (tuple(sorted([model1_name, model2_name])))


def get_url_file_ext(url):
    """Attempts to extract the file extension from the given URL."""
    # get the last part of the path component
    filename = url.split('/')[-1]
    _, ext = os.path.splitext(filename)
    return ext


def generate_quickstart(project_path):
    """Generates all of the basic paths for a Statik project within the given project path. If the project path
     doesn't exist, it will be created."""
    ensure_path_exists(project_path)
    ensure_file_exists(os.path.join(project_path, "config.yml"), DEFAULT_CONFIG_CONTENT)
    ensure_path_exists(os.path.join(project_path, 'models'))
    ensure_path_exists(os.path.join(project_path, 'data'))
    ensure_path_exists(os.path.join(project_path, 'templates'))
    ensure_path_exists(os.path.join(project_path, 'views'))
    ensure_path_exists(os.path.join(project_path, 'assets'))


def ensure_path_exists(path):
    if not os.path.isdir(path):
        logger.info('Creating path: %s' % path)
        os.makedirs(path)


def ensure_file_exists(path, default_content):
    if not os.path.isfile(path):
        logger.info('Creating file: %s' % path)
        with open(path, 'wt') as f:
            f.write(default_content)
