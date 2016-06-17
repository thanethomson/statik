# -*- coding:utf-8 -*-

import os
import os.path
import argparse
import logging

from statik.generator import generate

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
        '-i', '--input',
        help="The input path for the project to be built (default: current directory).",
    )
    parser.add_argument(
        '-o', '--output',
        help="The output path into which to place the built project (default: \"public\" directory in input directory).",
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Whether or not to output verbose logging information (default: false).",
        action='store_true',
    )
    args = parser.parse_args()
    input_path = args.input if args.input is not None else os.getcwd()
    output_path = args.output if args.output is not None else os.path.join(input_path, 'public')

    configure_logging(verbose=args.verbose)
    generate(input_path, output_path=output_path, in_memory=False)
