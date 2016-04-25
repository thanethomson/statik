# -*- coding:utf-8 -*-
"""
Asset management for Statik.
"""

import logging
import os.path
import shutil

import utils
from errors import *

logger = logging.getLogger(__name__)
__all__ = [
    "StatikAssetManager",
]


class StatikAssetManager:
    """Manager for Statik assets - files that will be copied as-is from the
    configured asset source path to the asset destination path (recursively)."""

    def __init__(self, src_path, dest_path, recursive=True, purge_dest=True):
        """Constructor.

        Args:
            src_path: The absolute source path from which assets are to be
                copied.
            dest_path: The absolute destination path to which assets are to
                be copied.
            recursive: Whether or not the copy is to be recursive.
            purge_dest: Whether or not to purge the destination directory
                prior to copying.
        """
        self._src_path = src_path
        self._dest_path = dest_path
        self._recursive = recursive
        self._purge_dest = purge_dest


    def copy(self):
        """Initiates the copy operation.

        Returns:
            The number of files copied.
        """
        # check that the source path exists
        if not os.path.isdir(self._src_path):
            raise PathNotDirectoryException("Asset source path cannot be found or accessed: %s" % self._src_path)

        # if the destination path already exists, and we have to purge it
        if os.path.isdir(self._dest_path) and self._purge_dest:
            logger.debug("Attempting to purge destination path: %s" % self._dest_path)
            # the easiest approach is to delete the entire tree and then
            # recreate it later
            shutil.rmtree(self._dest_path)

        logger.debug("Copying assets from %s to %s" % (self._src_path, self._dest_path))
        return utils.copy_tree(
            self._src_path,
            self._dest_path,
            recursive=self._recursive,
        )
