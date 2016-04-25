#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Central source file for Statik, the static web site generator.
"""

import logging
from project import StatikProject
from errors import *

logger = logging.getLogger(__name__)
__all__ = [
    "statik"
]


def statik(path, profile='production'):
    """Executes the Statik web site generator using the specified path as the
    working directory and source path.

    Args:
        path: The source path of the project to compile.
        profile: The name of the profile for which to build this project.

    Returns:
        The system exit value. This will be 0 on success, or non-zero on
        some kind of failure.
    """
    project = None

    logger.info("Attempting to load Statik project from path: %s" % path)
    try:
        project = StatikProject(path, profile=profile)
    except Exception as e:
        logger.exception("Caught exception while attempting to create project for path: %s" % path)
        return e.code if isinstance(e, StatikException) else 100

    logger.info("Project successfully loaded. Attempting to build project...")
    try:
        project.build()
    except Exception as e:
        logger.exception("Failed to build project")
        return e.code if isinstance(e, StatikException) else 101

    logger.info("Project successfully built.")
    # all's well that ends well
    return 0


def configure_logging(verbose=False):
    """Sets up the global configuration for our logging."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s' if verbose else "%(message)s",
    )


def main():
    """Main program routine, if this script is to be called as an
    executable from the command line."""
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--project",
        help="The path to the project to be processed.",
        default="./")
    parser.add_argument("-P", "--profile",
        help="Which profile to use for building the project.",
        default="production")
    parser.add_argument("-v", "--verbose",
        help="Enables debug (verbose) logging.",
        action="store_true")
    args = parser.parse_args()

    configure_logging(verbose=args.verbose)
    sys.exit(statik(args.project, profile=args.profile))


if __name__ == "__main__":
    main()
