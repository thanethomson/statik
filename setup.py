#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Setup script for Statik, the static web site generator.
"""

from setuptools import setup

INSTALL_REQUIREMENTS = [
    "jinja2==2.8",
    "PyYAML==3.11",
    "SQLAlchemy==1.0.13",
    "markdown==2.6.6"
]

setup(
    name="statik",
    version="0.2.5",
    description="General-purpose static web site generator",
    author="Thane Thomson",
    author_email="connect@thanethomson.com",
    url="https://github.com/thanethomson/statik",
    install_requires=INSTALL_REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'statik = statik.cmdline:main',
        ]
    },
    packages=["statik"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
    ]
)
