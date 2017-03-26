# -*- coding:utf-8 -*-

from __future__ import unicode_literals

__all__ = [
    'StatikError',
    'ReservedFieldNameError',
    'InvalidFieldTypeError',
    'MissingProjectFolderError',
    'MissingProjectConfig',
    'MissingParameterError',
    'DuplicateModelInstanceError',
    'InvalidModelCollectionDataError',
    'NoViewsError',
    'SafetyViolationError',
    'MissingTemplateError',
    'NoSupportedTemplateProvidersError'
]


class StatikError(Exception):
    """A generic error class."""
    exit_code = 1
    pass


class ReservedFieldNameError(StatikError):
    exit_code = 2
    pass


class InvalidFieldTypeError(StatikError):
    exit_code = 3
    pass


class MissingProjectFolderError(StatikError):
    exit_code = 4

    def __init__(self, folder, *args, **kwargs):
        super(MissingProjectFolderError, self).__init__(*args, **kwargs)
        self.folder = folder


class MissingProjectConfig(StatikError):
    exit_code = 5
    pass


class MissingParameterError(StatikError):
    exit_code = 6
    pass


class DuplicateModelInstanceError(StatikError):
    exit_code = 7
    pass


class InvalidModelCollectionDataError(StatikError):
    exit_code = 8
    pass


class NoViewsError(StatikError):
    exit_code = 9
    pass


class SafetyViolationError(StatikError):
    exit_code = 10
    pass


class MissingTemplateError(StatikError):
    exit_code = 11
    pass


class NoSupportedTemplateProvidersError(StatikError):
    exit_code = 12
    pass
