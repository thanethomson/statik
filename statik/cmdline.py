# -*- coding:utf-8 -*-

import os
import os.path
import argparse

from statik.generator import generate

__all__ = [
    'main',
]

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
    args = parser.parse_args()
    input_path = args.input if args.input is not None else os.getcwd()
    output_path = args.output if args.output is not None else os.path.join(input_path, 'public')

    print("Attempting to build project : %s" % input_path)
    print("Writing output to folder    : %s" % output_path)
    file_count = generate(input_path, output_path=output_path, in_memory=False)
    print("Number of files built       : %d" % file_count)
