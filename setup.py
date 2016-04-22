#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Setup script for Statik, the static web site generator.
"""

from distutils.core import setup

setup(
    name="statik",
    version="0.1.0",
    description="General-purpose static web site generator",
    author="Thane Thomson",
    author_email="connect@thanethomson.com",
    url="https://github.com/thanethomson/statik",
    scripts=["statik/statik"],
    packages=["statik", "statik.filters"],
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
