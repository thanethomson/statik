# -*- coding:utf-8 -*-

import os
import os.path


__all__ = [
    'list_files',
]


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
                (isinstance(ext, basestring) and entry_ext == ext) or \
                (isinstance(ext, list) and entry_ext in ext):
                files.append(entry)

    return files
