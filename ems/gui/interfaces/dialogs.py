
from abc import ABCMeta, abstractmethod

from six import add_metaclass

@add_metaclass(ABCMeta)
class FileDialog(object):

    @abstractmethod
    def openFileName(self, parent, windowTitle, filter, directory=None):
        pass

    @abstractmethod
    def openFileNames(self, parent, windowTitle, filter, directory=None):
        pass

    @abstractmethod
    def saveFileName(self, parent, windowTitle, filter, directory=None):
        pass

    @abstractmethod
    def existingDirectory(self, parent, windowTitle, directory):
        pass
