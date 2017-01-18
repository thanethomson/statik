#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Setup script for Statik, the static web site generator.
"""

import re
from io import open
import os.path
from setuptools import setup


def read_file(filename):
    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    with open(full_path, "rt", encoding="utf-8") as f:
        lines = f.readlines()
    return lines


def get_version():
    pattern = re.compile(r"__version__ = \"(?P<version>[0-9.a-zA-Z-]+)\"")
    for line in read_file(os.path.join("statik", "__init__.py")):
        m = pattern.match(line)
        if m is not None:
            return m.group('version')
    raise ValueError("Cannot extract version number for Statik")


setup(
    name="statik",
    version=get_version(),
    description="General-purpose static web site generator",
    long_description="".join(read_file("README.rst")),
    author="Thane Thomson",
    author_email="connect@thanethomson.com",
    url="https://getstatik.com",
    install_requires=[r.strip() for r in read_file("requirements.txt") if len(r.strip()) > 0],
    entry_points={
        'console_scripts': [
            'statik = statik.cmdline:main',
        ]
    },
    license='MIT',
    packages=["statik"],
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
    ]
)
