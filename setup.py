#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Setup script for Statik, the static web site generator.
"""

from setuptools import setup
from pip.req import parse_requirements

# work out our installation requirements from the requirements.txt file
install_reqs = parse_requirements("requirements.txt", session=False)

setup(
    name="statik",
    version="0.2.0",
    description="General-purpose static web site generator",
    author="Thane Thomson",
    author_email="connect@thanethomson.com",
    url="https://github.com/thanethomson/statik",
    install_requires=[str(ir.req) for ir in install_reqs],
    scripts=["statik/statik"],
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
