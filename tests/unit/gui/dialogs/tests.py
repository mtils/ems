
import os
import unittest

from ems.gui.interfaces.dialogs import AbstractFileDialog, ProxyFileDialog

class ProxyFileDialogTest(unittest.TestCase):

    def test_openFilename_forwards_to_adapter(self):
        fallback = fallbackDir()
        adapter = FakeFileDialog()
        proxy = ProxyFileDialog(adapter, fallback)

        params = ('parent', 'windowTitle', 'filter', 'dir')
        adapter.openFileReturn = 'return'
        fileName = proxy.openFileName(*params)
        self.assertEquals('return', fileName)
        self.assertEquals(params, adapter.openFileParams)
        ProxyFileDialog.lastPaths.clear()

    def test_openFilename_returns_fallback_if_no_directory_passed(self):
        fallback = fallbackDir()
        adapter = FakeFileDialog()
        proxy = ProxyFileDialog(adapter, fallback)

        params = ('parent', 'windowTitle', 'filter', None)
        awaitedParams = (params[0], params[1], params[2], fallback)
        adapter.openFileReturn = 'return'
        fileName = proxy.openFileName(*params)
        self.assertEquals('return', fileName)
        self.assertEquals(awaitedParams, adapter.openFileParams)
        ProxyFileDialog.lastPaths.clear()

    def test_openFilename_returns_last_parent_directory_if_no_directory_passed(self):
        fallback = fallbackDir()
        adapter = FakeFileDialog()
        proxy = ProxyFileDialog(adapter, fallback)

        fileDir = findDir()
        fileName = findFile(fileDir)

        params = ('parent', 'windowTitle', 'filter', None)
        awaitedParams = (params[0], params[1], params[2], fallback)
        adapter.openFileReturn = fileName
        self.assertEquals(proxy.openFileName(*params), fileName)
        self.assertEquals(awaitedParams, adapter.openFileParams)

        awaitedParams = (params[0], params[1], params[2], fileDir)

        otherFileName = findFile(fallback)

        adapter.openFileReturn = otherFileName
        self.assertEquals(proxy.openFileName(*params), otherFileName)

        ProxyFileDialog.lastPaths.clear()

    def test_openFilenames_forwards_to_adapter(self):
        fallback = fallbackDir()
        adapter = FakeFileDialog()
        proxy = ProxyFileDialog(adapter, fallback)

        params = ('parent', 'windowTitle', 'filter', 'dir')
        adapter.openFileReturn = 'return'
        fileName = proxy.openFileName(*params)
        self.assertEquals('return', fileName)
        self.assertEquals(params, adapter.openFileParams)
        ProxyFileDialog.lastPaths.clear()
class FakeFileDialog(AbstractFileDialog):

    def __init__(self):
        self.openFileReturn = None
        self.openFileParams = None
        self.openFilesReturn = None
        self.openFilesParams = None
        self.saveFileReturn = None
        self.saveFileParams = None
        self.existingDirReturn = None
        self.existingDirParams = None

    def openFileName(self, parent, windowTitle, filter, directory=None):
        self.openFileParams = (parent, windowTitle, filter, directory)
        return self.openFileReturn

    def openFileNames(self, parent, windowTitle, filter, directory=None):
        self.openFilesParams = (parent, windowTitle, filter, directory)
        return self.openFilesReturn

    def saveFileName(self, parent, windowTitle, filter, directory=None):
        self.saveFileParams = (parent, windowTitle, filter, directory)
        return self.saveFileReturn

    def existingDirectory(self, parent, windowTitle, directory=None):
        self.existingDirParams = (parent, windowTitle, directory)
        return self.existingDirReturn

def findDir():
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def fallbackDir():
    return os.path.abspath(os.path.dirname(findDir()))

def findFile(directory):
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            return path

if __name__ == '__main__':
    unittest.main()