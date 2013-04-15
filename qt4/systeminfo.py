
from PyQt4.QtCore import QObject
from PyQt4.QtGui import QImageReader

class SystemInfo(object):
    
    Image = 1
    
    @staticmethod
    def getSupportedExtensions(fileType):
        if fileType == SystemInfo.Image:
            result = []
            for format in QImageReader.supportedImageFormats():
                result.append(unicode(format))
            return result

    @staticmethod
    def buildFilterString(extensionList):
        extStringList = []
        for ext in extensionList:
            extStringList.append(u"*.{0}".format(ext))
        return "(" + u" ".join(extStringList) + ")"