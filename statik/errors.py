# -*- coding:utf-8 -*-

__all__ = [
    'ReservedFieldNameError',
    'InvalidFieldTypeError',
    'MissingProjectFolderError',
    'MissingParameterError',
    'DuplicateModelInstanceError',
    'InvalidModelCollectionDataError',
    'NoViewsError',
]


class ReservedFieldNameError(ValueError):
    pass


class InvalidFieldTypeError(ValueError):
    pass


class MissingProjectFolderError(ValueError):
    def __init__(self, folder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder = folder


class MissingParameterError(ValueError):
    pass


class DuplicateModelInstanceError(ValueError):
    pass


class InvalidModelCollectionDataError(ValueError):
    pass


class NoViewsError(Exception):
    pass
