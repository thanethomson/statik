#!/bin/bash
rm dist/*
python setup.py sdist bdist_wheel
rm dist/*.egg
twine upload dist/*

