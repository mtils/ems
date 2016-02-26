
import os
from abc import ABCMeta, abstractmethod

from six import add_metaclass

from ems.typehint import accepts
from ems.util import classproperty
from ems.event.hook import EventHookProperty

@add_metaclass(ABCMeta)
class AbstractFileDialog(object):

    currentChanged = EventHookProperty()
    """
    This event is fired when the user choosed a file
    (Not only selected)
    signature: currentChanged(str)
    """

    directoryEntered = EventHookProperty()
    """
    This event is fired when the user enters a directory
    signature: directoryEntered(str)
    """

    filesSelected = EventHookProperty()
    """
    The is fired if the user can select multiple files and the selection
    does change
    signature: filesSelected([])
    """

    filterSelected = EventHookProperty()
    """
    This is fired if the user selects a filter (e.g. Image Files or Documents)
    signature: filterSelected(str)
    """

    @abstractmethod
    def openFileName(self, parent, windowTitle, filter, directory=None):
        """
        Ask the user for a filename of an existing file
        :returns: The filename as a string or None if no one was selected
        """
        pass

    @abstractmethod
    def openFileNames(self, parent, windowTitle, filter, directory=None):
        """
        Ask the user for one or many filenames
        :returns: The filenames as a tuple, set or list and an empty if no file selected
        """
        pass

    @abstractmethod
    def saveFileName(self, parent, windowTitle, filter, directory=None):
        """
        Ask the user for a filename to save a file
        :returns: The filename as a string or None if no one was selected
        """
        pass

    @abstractmethod
    def existingDirectory(self, parent, windowTitle, directory=None):
        """
        Ask the user for an existing directory
        :returns: The dirname as a string or None if no one was selected
        """
        pass

class FileDialog(AbstractFileDialog):
    """
    This class is just a placeholder to register the ProxyFileDialog in your
    app.
    Register the toolkit adapter via
    app.bind(AbstractFileDialog, YourClass) and the proxy:
    app.bind(FileDialog, app(ProxyFileDialog))
    """
    pass

class ProxyFileDialog(AbstractFileDialog):
    """
    The ProxyFileDialog will be used in your application. It fires its events
    and allows to memorize the last directory
    """

    lastPaths = {}

    @accepts(AbstractFileDialog)
    def __init__(self, adapterFileDialog, fallbackDirectory=None):
        self.context = None
        self.adapter = adapterFileDialog
        self.fallbackDirectory = fallbackDirectory


    def openFileName(self, parent, windowTitle, filter, directory=None):
        """
        Ask the user for a filename of an existing file
        :returns: The filename as a string or None if no one was selected
        """
        directory = self._chooseDirectory(directory)
        fileName = self.adapter.openFileName(parent, windowTitle, filter, directory)
        if not fileName:
            return None

        self._storeLastDir(fileName)
        self.filesSelected.fire((fileName,))

        return fileName

    def openFileNames(self, parent, windowTitle, filter, directory=None):
        """
        Ask the user for one or many filenames
        :returns: The filenames as a tuple, set or list and an empty if no file selected
        """
        directory = self._chooseDirectory(directory)
        fileNames = self.adapter.openFileNames(parent, windowTitle, filter, directory)
        if not fileNames:
            return None

        self._storeLastDir(fileNames[0])
        self.filesSelected.fire(fileNames)

    def saveFileName(self, parent, windowTitle, filter, directory=None):
        """
        Ask the user for a filename to save a file
        :returns: The filename as a string or None if no one was selected
        """
        directory = self._chooseDirectory(directory)
        fileName = self.adapter.saveFileName(parent, windowTitle, filter, directory)
        if not fileName:
            return None

        self._storeLastDir(fileName)
        self.filesSelected.fire((fileName,))

        return fileName

    def existingDirectory(self, parent, windowTitle, directory=None):
        """
        Ask the user for an existing directory
        :returns: The dirname as a string or None if no one was selected
        """
        directory = self._chooseDirectory(directory)
        dirName = self.adapter.existingDirectory(parent, windowTitle, directory)
        if not dirName:
            return None

        self._storeLastDir(dirName)
        self.directoryEntered.fire(dirName)

        return dirName

    def __getitem__(self, context):
        """
        Return an instance of the filemanager for context. This is used to
        autoselect the last used directory in this context.
        e.g.:
        app(FileDialog)['images'].saveFileName()
        """
        proxy = self._copyInstance()
        proxy.context = context
        return proxy

    def _copyInstance(self):
        return self.__class__(self.adapter, self.fallbackDirectory)

    def _storeLastDir(self, path):
        context = "" if self.context is None else self.context
        ProxyFileDialog.lastPaths[context] = self._dirOfPath(path)

    def _chooseDirectory(self, passedDirectory):
        if passedDirectory:
            return passedDirectory
        if self.context in ProxyFileDialog.lastPaths:
            return ProxyFileDialog.lastPaths[self.context]
        return self.fallbackDirectory

    def _dirOfPath(self, path):
        return path if os.path.isdir(path) else os.path.dirname(path)