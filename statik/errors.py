# -*- coding:utf-8 -*-
"""All of the relevant exceptions for Statik organised in one place."""

__all__ = [
    "StatikException",
    "InvalidPathException",
    "PathNotDirectoryException",
    "MissingConfigException",
    "InvalidConfigException",
    "InvalidViewConfigException",
    "MissingInstanceException",
    "InvalidFieldTypeException",
    "InvalidModelConfigException",
    "UnsupportedDataFileException",
    "InvalidDataException",
    "ModelDoesNotExistException",
    "CircularDependencyException",
    "MissingDatabaseException",
]

class StatikException(Exception):
    """Base exception class for all Statik exceptions."""

    code = 1

    def __init__(self, msg, code=None):
        """Constructor.

        Args:
            msg: The exception message.
            code: The system exit code to use if this is a terminal error.
        """
        super(StatikException, self).__init__(msg)
        if code is not None:
            self.code = code


class InvalidPathException(StatikException):
    code = 1

class PathNotDirectoryException(StatikException):
    code = 2

class MissingConfigException(StatikException):
    code = 3

class InvalidConfigException(StatikException):
    code = 4

class InvalidViewConfigException(StatikException):
    code = 5

class MissingInstanceException(StatikException):
    code = 6

class InvalidFieldTypeException(StatikException):
    code = 7

class InvalidModelConfigException(StatikException):
    code = 8

class UnsupportedDataFileException(StatikException):
    code = 9

class InvalidDataException(StatikException):
    code = 10

class ModelDoesNotExistException(StatikException):
    code = 11

class CircularDependencyException(StatikException):
    code = 12

class MissingDatabaseException(StatikException):
    code = 13
