# -*- coding:utf-8 -*-

import os
import os.path
import argparse

from statik.generator import generate
from statik.utils import generate_quickstart
from statik.watcher import watch

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'main',
]


def configure_logging(verbose=False):
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s' if verbose else "%(message)s",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Statik, the static web site generator for developers."
    )
    parser.add_argument(
        '-p', '--project',
        help="The path to your Statik project (default: current directory).",
    )
    parser.add_argument(
        '-o', '--output',
        help="The output path into which to place the built project (default: \"public\" directory in input " +
             "directory).",
    )
    parser.add_argument(
        '-w', '--watch',
        help="Statik will watch the project path for changes and automatically regenerate the project. " +
            "This also runs a small HTTP server to serve your output files.",
        action='store_true',
    )
    parser.add_argument(
        '--host',
        help="When watching a folder for changes (--watch), this specifies the host IP address or hostname to which " +
             "to bind (default: localhost).",
        default='localhost',
    )
    parser.add_argument(
        '--port',
        help="When watching a folder for changes (--watch), this specifies the port to which to bind (default: 8000).",
        type=int,
        default=8000,
    )
    parser.add_argument(
        '--quickstart',
        help="Statik will generate a basic directory structure for you in the project directory.",
        action='store_true',
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Whether or not to output verbose logging information (default: false).",
        action='store_true',
    )
    parser.add_argument(
        '--version',
        help='Display version info for Statik',
        action='store_true',
    )
    args = parser.parse_args()
    project_path = args.project if args.project is not None else os.getcwd()
    output_path = args.output if args.output is not None else os.path.join(project_path, 'public')

    configure_logging(verbose=args.verbose)
    if args.version:
        from statik import STATIK_VERSION
        logger.info('Statik v%s' % STATIK_VERSION)
    elif args.watch:
        watch(project_path, output_path, host=args.host, port=args.port)
    elif args.quickstart:
        generate_quickstart(project_path)
    else:
        generate(project_path, output_path=output_path, in_memory=False)


if __name__ == "__main__":
    main()
