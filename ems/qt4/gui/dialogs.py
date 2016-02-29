
from PyQt4.QtGui import QFileDialog

from six import u

from ems.gui.interfaces.dialogs import AbstractFileDialog

class Qt4FileDialog(AbstractFileDialog):

    def openFileName(self, parent, windowTitle, filter, directory=None):
        """
        Ask the user for a filename of an existing file
        :returns: The filename as a string or None if no one was selected
        """
        fileName = QFileDialog.getOpenFileName(parent, windowTitle, directory, filter)

        if fileName:
            return u(fileName)

    def openFileNames(self, parent, windowTitle, filter, directory=None):
        """
        Ask the user for one or many filenames
        :returns: The filenames as a tuple, set or list and an empty if no file selected
        """
        fileNames = QFileDialog.getOpenFileNames(parent, windowTitle, directory, filter)
        if not fileNames:
            return ()
        names = []
        for fileName in fileNames:
            names.append(u(fileName))

        return names

    def saveFileName(self, parent, windowTitle, filter, directory=None):
        """
        Ask the user for a filename to save a file
        :returns: The filename as a string or None if no one was selected
        """
        fileName = QFileDialog.getSaveFileName(parent, windowTitle, directory, filter)
        if fileName:
            return u(fileName)

    def existingDirectory(self, parent, windowTitle, directory=None):
        """
        Ask the user for an existing directory
        :returns: The dirname as a string or None if no one was selected
        """
        dirName = QFileDialog.getExistingDirectory(parent, windowTitle, directory)
        if dirName:
            return u(dirName)