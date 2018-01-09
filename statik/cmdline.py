# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os
import os.path
import argparse
import sys
import shutil

import colorlog

from statik.generator import generate
from statik.utils import generate_quickstart, get_project_config_file
from statik.watcher import watch
from statik.project import StatikProject
from statik.errors import StatikError, StatikErrorContext

import logging
logger = logging.getLogger(__name__)

__all__ = [
    'main',
]


def configure_logging(verbose=False, quiet=False, fail_silently=False, colourise=True):
    handler = colorlog.StreamHandler() if colourise else logging.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s' + (
            '%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s' if verbose else '%(message)s'
        )
    ) if colourise else logging.Formatter(
        '%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s' if verbose else '%(message)s'
    )
    handler.setFormatter(formatter)
    root_logger = logging.getLogger("")
    root_logger.addHandler(handler)
    root_logger.setLevel(
        logging.CRITICAL if quiet and fail_silently else
        logging.ERROR if quiet else
        logging.DEBUG if verbose else
        logging.INFO
    )


def show_version():
    from statik import __version__
    logger.info('Statik v%s', __version__)


def main():
    parser = argparse.ArgumentParser(
        description="Statik: a static web site generator for developers."
    )
    parser.add_argument(
        '--version',
        help='Display version info for Statik',
        action='store_true',
    )
    parser.add_argument(
        '--quickstart',
        help="Statik will generate a basic directory structure for you in the project directory and exit.",
        action='store_true',
    )
    parser.add_argument(
        '-p', '--project',
        help="The path to your Statik project or project YAML configuration file (default: current directory).",
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
        '-n', '--no-browser',
        action='store_true',
        default=False,
        help="Do not attempt to automatically open a web browser at the served URL when watching for changes"
    )
    parser.add_argument(
        '-s', '--safe-mode',
        action='store_true',
        default=False,
        help="Run Statik in safe mode (which disallows unsafe query execution)"
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Whether or not to output verbose logging information (default: false).",
        action='store_true',
    )
    parser.add_argument(
        '--quiet',
        default=False,
        help="Run Statik in quiet mode, where there will be no output except upon error.",
        action='store_true'
    )
    parser.add_argument(
        '--fail-silently',
        default=False,
        help="Only relevant if running Statik in quiet mode - if Statik encounters an error, the only indication "
             "of this will be in the resulting error code returned by the process. No other output will be given "
             "on the terminal.",
        action='store_true'
    )
    parser.add_argument(
        '--no-colorlog',
        action='store_true',
        help="By default, Statik outputs logging data in colour. By specifying this switch, " +
             "coloured logging will be turned off."
    )
    parser.add_argument(
        '--clear-output',
        action='store_true',
        help="Clears the output folder first prior to building the project. If watching " +
            "is initiated, this will only clear the output folder once-off."
    )
    args = parser.parse_args()

    error_context = StatikErrorContext()
    try:
        _project_path = args.project if args.project is not None else os.getcwd()
        project_path, config_file_path = get_project_config_file(
            _project_path,
            StatikProject.CONFIG_FILE
        )
        output_path = args.output if args.output is not None else \
            os.path.join(project_path, 'public')

        configure_logging(
            verbose=args.verbose,
            quiet=args.quiet,
            fail_silently=args.fail_silently,
            colourise=not args.no_colorlog
        )

        if args.fail_silently and not args.quiet:
            logger.warning("Ignoring --fail-silently switch because --quiet is not specified")

        if args.version:
            show_version()
            sys.exit(0)

        if args.clear_output:
            shutil.rmtree(output_path, ignore_errors=True)
            logger.info("Cleared output path: %s", output_path)

        if args.watch:
            watch(
                config_file_path,
                output_path,
                host=args.host,
                port=args.port,
                open_browser=(not args.no_browser),
                safe_mode=args.safe_mode,
                error_context=error_context
            )
        elif args.quickstart:
            generate_quickstart(project_path)
        else:
            generate(
                config_file_path,
                output_path=output_path,
                in_memory=False,
                safe_mode=args.safe_mode,
                error_context=error_context
            )

    except StatikError as e:
        sys.exit(e.exit_code)

    except Exception as e:
        logger.exception("Exception caught while attempting to generate project")
        sys.exit(1)

    # success
    sys.exit(0)


if __name__ == "__main__":
    main()
