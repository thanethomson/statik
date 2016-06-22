# -*- coding:utf-8 -*-

import os
import os.path
import argparse
import logging

from statik.generator import generate
from statik.utils import generate_quickstart

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
        '--quickstart',
        help="Statik will generate a basic directory structure for you in the project directory.",
        action='store_true',
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Whether or not to output verbose logging information (default: false).",
        action='store_true',
    )
    args = parser.parse_args()
    project_path = args.project if args.project is not None else os.getcwd()
    output_path = args.output if args.output is not None else os.path.join(project_path, 'public')

    configure_logging(verbose=args.verbose)
    if args.quickstart:
        generate_quickstart(project_path)
    else:
        generate(project_path, output_path=output_path, in_memory=False)
