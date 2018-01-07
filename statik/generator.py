# -*- coding:utf-8 -*-

from __future__ import unicode_literals
from statik.project import StatikProject

__all__ = [
    "generate",
]


def generate(input_path, output_path=None, in_memory=False, safe_mode=False, error_context=None):
    """Executes the Statik site generator using the given parameters.
    """
    project = StatikProject(input_path, safe_mode=safe_mode, error_context=error_context)
    return project.generate(output_path=output_path, in_memory=in_memory)
