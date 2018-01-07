# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os.path
import httpwatcher

from statik.project import StatikProject
from statik.errors import StatikError, MissingProjectFolderError, StatikErrorContext

import logging
logger = logging.getLogger(__name__)


__all__ = [
    "watch",
]


def safe_wrap_project_generate(project, output_path):
    try:
        logger.info("")
        project.generate(output_path=output_path, in_memory=False)
        logger.info("")
    except:
        pass


def watch(project_path, output_path, host='0.0.0.0', port=8000, min_reload_time=2.0,
          open_browser=True, safe_mode=False, error_context=None):
    """Watches the given project path for filesystem changes, and automatically rebuilds the project when
    changes are detected. Also serves an HTTP server on the given host/port.

    Args:
        project_path: The path to the Statik project to be watched.
        output_path: The path into which to write the output files.
        host: The host IP/hostname to which to bind when serving output files.
        port: The port to which to bind when serving output files.
        min_reload_time: The minimum time (in seconds) between reloads when files change.
        open_browser: Whether or not to automatically open the web browser at the served URL.
        safe_mode: Whether or not to run Statik in safe mode.
        error_context: An optional StatikErrorContext instance for detailed error reporting.
    """
    error_context = error_context or StatikErrorContext()
    project = StatikProject(project_path, safe_mode=safe_mode, error_context=error_context)
    project.generate(output_path=output_path, in_memory=False)

    watch_folders = [
        StatikProject.MODELS_DIR,
        StatikProject.DATA_DIR,
        StatikProject.VIEWS_DIR,
        StatikProject.TEMPLATES_DIR,
        project.config.assets_src_path
    ]

    # let the template tags folder be optional
    template_tags_folder = os.path.join(project.path, StatikProject.TEMPLATETAGS_DIR)
    if os.path.exists(template_tags_folder) and os.path.isdir(template_tags_folder):
        watch_folders.append(StatikProject.TEMPLATETAGS_DIR)

    # if theming is enabled, watch the specific theme's folder for changes
    if project.config.theme is not None:
        watch_folders.append(os.path.join(StatikProject.THEMES_DIR, project.config.theme))

    watch_folders = [f if os.path.isabs(f) else os.path.join(project.path, f) for f in watch_folders]
    for folder in watch_folders:
        if not os.path.exists(folder) or not os.path.isdir(folder):
            raise MissingProjectFolderError(folder)

    httpwatcher.watch(
        output_path,
        watch_paths=watch_folders,
        on_reload=lambda: safe_wrap_project_generate(
            project,
            output_path
        ),
        host=host,
        port=port,
        server_base_path=project.config.base_path,
        watcher_interval=min_reload_time,
        recursive=True,
        open_browser=open_browser
    )
