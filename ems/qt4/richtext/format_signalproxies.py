
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal, QString, pyqtProperty
from PyQt4.QtGui import QTextFormat, QTextCharFormat, QFont, QFontInfo

class TextFormatSignalProxy(QObject):
    pass

class CharFormatSignalProxy(QObject):

    fontChanged = pyqtSignal(QFont)

    fontFamilyChanged = pyqtSignal(QString)

    boldChanged = pyqtSignal(bool)

    italicChanged = pyqtSignal(bool)

    underlineChanged = pyqtSignal(bool)

    pixelSizeChanged = pyqtSignal(int)

    pointSizeChanged = pyqtSignal(int)

    isAnchorChanged = pyqtSignal(bool)

    anchorChanged = pyqtSignal(QString)

    def __init__(self, parent=None):
        super(CharFormatSignalProxy, self).__init__(parent)
        self._charFormat = None
        self._isAnchor = False
        self._anchor = ''

    def getCharFormat(self):
        return self._charFormat

    @pyqtSlot(QTextCharFormat)
    def setCharFormat(self, charFormat):
        oldCharFormat = self._charFormat
        if self._charFormatsAreEqual(oldCharFormat, charFormat):
            return
        self._charFormat = charFormat
        self.setFont(charFormat.font())

    charFormat = pyqtProperty(QTextCharFormat, getCharFormat, setCharFormat)

    def getFont(self):
        return self._charFormat.font()

    @pyqtSlot(QFont)
    def setFont(self, newFont):
        currentFont = self._charFormat.font()
        if currentFont == newFont:
            return

        self._charFormat.setFont(newFont)
        self.fontChanged.emit(newFont)

        newFontFamily = QFontInfo(newFont).family()

        if newFontFamily != QFontInfo(currentFont).family():
            self.fontFamilyChanged.emit(newFontFamily)

        if newFont.bold() != currentFont.bold():
            self.boldChanged.emit(newFont.bold())

        if newFont.italic() != currentFont.italic():
            self.italicChanged.emit(newFont.italic())

        if newFont.underline() != currentFont.underline():
            self.underlineChanged.emit(newFont.underline())

        if newFont.pointSize() != currentFont.pointSize():
            self.pointSizeChanged.emit(newFont.pointSize())

    font = pyqtProperty(QFont, getFont, setFont)

    def getFontFamily(self):
        return QFontInfo(self.getFont()).family()

    @pyqtSlot(QString)
    def setFontFamily(self, family):
        if self.getFontFamily() == family:
            return
        currentFont = self._charFormat.font()
        newFont = QFont(family)
        newFont.setBold(currentFont.bold())
        newFont.setItalic(currentFont.italic())
        newFont.setUnderline(currentFont.underline())
        newFont.setPointSizeF(currentFont.pointSizeF())
        self.setFont(newFont)

    fontFamily = pyqtProperty(QString, getFontFamily, setFontFamily)

    def getBold(self):
        return self._charFormat.font.bold()

    @pyqtSlot(bool)
    def setBold(self, bold):
        if self.getBold() == bold:
            return
        newFont = QFont(self._charFormat.font())
        newFont.setBold(bold)
        self.setFont(newFont)

    bold = pyqtProperty(bool, getBold, setBold)

    def getItalic(self):
        return self._charFormat.font().italic()

    @pyqtSlot(bool)
    def setItalic(self, italic):
        if self.getItalic() == italic:
            return
        newFont = QFont(self._charFormat.font())
        newFont.setItalic(italic)
        self.setFont(newFont)

    italic = pyqtProperty(bool, getItalic, setItalic)

    def getUnderline(self):
        return self._charFormat.font().underline()

    @pyqtSlot(bool)
    def setUnderline(self, underline):
        if self.getUnderline() == underline:
            return
        newFont = QFont(self._charFormat.font())
        newFont.setUnderline(underline)
        self.setFont(newFont)

    underline = pyqtProperty(bool, getUnderline, setUnderline)

    def getPointSize(self):
        return self._charFormat.font().pointSize()

    def setPointSize(self, pointSize):
        if self.getPointSize() == pointSize:
            return
        newFont = QFont(self._charFormat.font())
        newFont.setPointSize(pointSize)
        self.setFont(newFont)

    pointSize = pyqtProperty(int, getPointSize, setPointSize)

    def _charFormatsAreEqual(self, left, right):
        if left.font() != right.font():
            return False
        if left.isAnchor() != right.isAnchor():
            return False
        if left.anchorHref() != right.anchorHref():
            return False
        return True