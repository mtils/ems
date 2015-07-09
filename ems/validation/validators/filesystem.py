
import os

from abc import ABCMeta, abstractmethod

from ems.typehint import accepts
from ems.validation.abstract import Validator

class PathNormalizer(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def normalize(self, path):
        pass

class NullNormalizer(PathNormalizer):

    def normalize(self, path):
        return path

class FileExistsValidator(Validator):

    def __init__(self, normalizer=None):
        self._normalizer = NullNormalizer() if normalizer is None else normalizer

    def validate(self, value):
        return os.path.isfile(self._normalizer.normalize(value))

class DirExistsValidator(Validator):

    def __init__(self, normalizer=None):
        self._normalizer = NullNormalizer() if normalizer is None else normalizer

    def validate(self, value):
        return os.path.isdir(self._normalizer.normalize(value))

class NewFileValidator(FileExistsValidator):
    def validate(self, value):
        return not super(NewFileValidator, self).validate(value)

class NewDirValidator(DirExistsValidator):
    def validate(self, value):
        return not super(NewDirValidator, self).validate(value)

class ExtensionValidator(Validator):
    def validate(self, value, *args):
        try:
            return (os.path.splitext(value)[1][1:] in args)
        except IndexError:
            return False

class AppFileExistsValidator(FileExistsValidator):
    @accepts(PathNormalizer)
    def __init__(self, normalizer=None):
        super(AppFileExistsValidator, self).__init__(normalizer)

class AppDirExistsValidator(DirExistsValidator):
    @accepts(PathNormalizer)
    def __init__(self, normalizer=None):
        super(AppDirExistsValidator, self).__init__(normalizer)


class NewAppFileValidator(NewFileValidator):
    @accepts(PathNormalizer)
    def __init__(self, normalizer=None):
        super(NewAppFileValidator, self).__init__(normalizer)

class NewAppDirValidator(NewDirValidator):
    @accepts(PathNormalizer)
    def __init__(self, normalizer=None):
        super(NewAppDirValidator, self).__init__(normalizer)

