# -*- coding:utf-8 -*-

__all__ = [
    'InvalidFieldTypeError',
    'MissingProjectFolderError',
    'MissingParameterError',
    'DuplicateModelInstanceError',
]

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
