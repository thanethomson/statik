# -*- coding:utf-8 -*-

import os.path
import time

from livereload import Server

from statik.generator import generate
from statik.project import StatikProject
from statik.config import StatikConfig
from statik.utils import get_project_config_file

import logging
logger = logging.getLogger(__name__)


__all__ = [
    "watch",
]


class StatikWatcher(object):
    """Helper class for keeping track of our re-generation operations."""

    def __init__(self, project_path, output_path, min_reload_time=2.0):
        self.project_path = project_path
        self.output_path = output_path
        self.min_reload_time = min_reload_time
        self.last_generated = 0
        logger.debug("Watching project path: %s" % self.project_path)
        logger.debug("Output path: %s" % self.output_path)

    def generator_factory(self, folder):
        """Produces a function that can be called by the folder watcher to regenerate the project based on changes
        from the specific folder we're watching here."""
        logger.debug("Adding generator function for target: %s" % folder)

        def do_generate():
            now = time.time()
            if (now - self.last_generated) >= self.min_reload_time:
                logger.info("Regenerating project from change in path: %s" % folder)
                self.generate()
            else:
                logger.warn("Minimum time between successive hot reloads is %.2fs" % self.min_reload_time)
            self.last_generated = now

        return do_generate

    def generate(self):
        generate(self.project_path, self.output_path, in_memory=False)


def watch(project_path, output_path, host='0.0.0.0', port=8000, min_reload_time=2.0):
    """Watches the given project path for filesystem changes, and automatically rebuilds the project when
    changes are detected. Also serves an HTTP server on the given host/port.

    Args:
        project_path: The path to the Statik project to be watched.
        output_path: The path into which to write the output files.
        host: The host IP/hostname to which to bind when serving output files.
        port: The port to which to bind when serving output files.
        min_reload_time: The minimum time (in seconds) between reloads when files change.
    """
    _project_path, config_file = get_project_config_file(project_path, StatikProject.CONFIG_FILE)
    watcher = StatikWatcher(config_file, output_path, min_reload_time=min_reload_time)
    # generate once-off before starting the server
    watcher.generate()

    config = StatikConfig(config_file)
    watch_folders = [
        StatikProject.MODELS_DIR,
        StatikProject.DATA_DIR,
        StatikProject.TEMPLATES_DIR,
        StatikProject.VIEWS_DIR,
        StatikProject.TEMPLATETAGS_DIR,
        config.assets_src_path,
    ]
    watch_folders = [f if os.path.isabs(f) else os.path.join(_project_path, f) for f in watch_folders]
    server = Server()
    for f in watch_folders:
        server.watch(f, func=watcher.generator_factory(f))

    logger.info("Serving content from %s at http://%s:%d" % (output_path, host, port))
    server.serve(root=output_path, host=host, port=port)
    logger.info("Stopped server")
