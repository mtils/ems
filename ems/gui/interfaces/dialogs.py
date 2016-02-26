
from abc import ABCMeta, abstractmethod

from six import add_metaclass

from ems.event.hook import EventHookProperty

@add_metaclass(ABCMeta)
class FileDialog(object):

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

    fileSelected = EventHookProperty()
    """
    This event is fired when the user selects a file (before choosing)
    signature: fileSelected(str)
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
    def existingDirectory(self, parent, windowTitle, directory):
        """
        Ask the user for an existing directory
        :returns: The dirname as a string or None if no one was selected
        """
        pass

    @abstractmethod
    def __getitem__(self, context):
        """
        Return an instance of the filemanager for context. This is used to
        autoselect the last used directory in this context.
        e.g.:
        app(FileDialog)['images'].saveFileName()
        """
        pass

    def _copyInstance(self):
        return self.__class__()