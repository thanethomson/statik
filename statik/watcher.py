# -*- coding:utf-8 -*-

import os.path

from livereload import Server

from statik.generator import generate
from statik.project import StatikProject
from statik.config import StatikConfig

import logging
logger = logging.getLogger(__name__)


__all__ = [
    "watch",
]


def watch(project_path, output_path, host='0.0.0.0', port=8000):
    """Watches the given project path for filesystem changes, and automatically rebuilds the project when
    changes are detected. Also serves an HTTP server on the given host/port."""
    # first run a generate operation on the project
    generate(project_path, output_path=output_path, in_memory=False)

    config_file = os.path.join(project_path, StatikProject.CONFIG_FILE)
    config = StatikConfig(config_file)
    watch_folders = [
        StatikProject.MODELS_DIR,
        StatikProject.DATA_DIR,
        StatikProject.TEMPLATES_DIR,
        StatikProject.VIEWS_DIR,
        config.assets_src_path,
    ]
    watch_folders = [f if os.path.isabs(f) else os.path.join(project_path, f) for f in watch_folders]
    server = Server()
    for f in watch_folders:
        server.watch(f, lambda: generate(project_path, output_path=output_path, in_memory=False))

    logger.info("Serving content from %s at http://%s:%d" % (output_path, host, port))
    server.serve(root=output_path, host=host, port=port)
    logger.info("Stopped server")
