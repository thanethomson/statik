# -*- coding:utf-8 -*-

from __future__ import unicode_literals

__all__ = [
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


class ReservedFieldNameError(ValueError):
    pass


class InvalidFieldTypeError(ValueError):
    pass


class MissingProjectFolderError(ValueError):
    def __init__(self, folder, *args, **kwargs):
        super(MissingProjectFolderError, self).__init__(*args, **kwargs)
        self.folder = folder


class MissingProjectConfig(Exception):
    pass


class MissingParameterError(ValueError):
    pass


class DuplicateModelInstanceError(ValueError):
    pass


class InvalidModelCollectionDataError(ValueError):
    pass


class NoViewsError(Exception):
    pass


class SafetyViolationError(Exception):
    pass


class MissingTemplateError(Exception):
    pass


class NoSupportedTemplateProvidersError(Exception):
    pass
