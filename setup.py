#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Setup script for Statik, the static web site generator.
"""

from setuptools import setup
from statik import __version__

INSTALL_REQUIREMENTS = [
    "jinja2==2.8",
    "PyYAML==3.11",
    "SQLAlchemy==1.0.14",
    "markdown==2.6.6",
    "livereload==2.4.1",
]

setup(
    name="statik",
    version=__version__,
    description="General-purpose static web site generator",
    author="Thane Thomson",
    author_email="connect@thanethomson.com",
    url="https://getstatik.com",
    install_requires=INSTALL_REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'statik = statik.cmdline:main',
        ]
    },
    packages=["statik"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
    ]
)
