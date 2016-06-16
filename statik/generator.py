# -*- coding:utf-8 -*-

from statik.project import StatikProject

__all__ = [
    "generate",
]


def generate(input_path, output_path=None, in_memory=False):
    """Executes the Statik site generator using the given parameters.
    """
    project = StatikProject(input_path)
    return project.generate(output_path=output_path, in_memory=in_memory)
