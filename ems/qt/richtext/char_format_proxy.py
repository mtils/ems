
from six import text_type

from ems.qt import QtCore
from ems.qt import QtGui

QObject = QtCore.QObject
pyqtSlot = QtCore.pyqtSlot
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
Qt = QtCore.Qt
QTextCharFormat = QtGui.QTextCharFormat
QFont = QtGui.QFont
QFontInfo = QtGui.QFontInfo
QBrush = QtGui.QBrush
QColor = QtGui.QColor


class CharFormatProxy(QObject):

    charFormatChanged = pyqtSignal(QTextCharFormat)
    '''
    This signal is emitted if a new charFormat is setted.
    Setting a new format emits all other signals
    '''

    charFormatModified = pyqtSignal(QTextCharFormat)
    '''
    This signal is emitted if some property of the charFormat or its font or
    brushes (foreground/background) was changed
    '''

    charFormatDiffChanged = pyqtSignal(QTextCharFormat)
    '''
    This signal is emitted everytime charFormatModified is emitted. The only
    difference is that only an empty QTextCharFormat only with the changed
    property is emitted. This is usefull to use with QTextEdit.mergeCurrentCharFormat
    '''

    fontChanged = pyqtSignal(QFont)
    '''
    '''

    fontFamilyChanged = pyqtSignal(text_type)

    boldChanged = pyqtSignal(bool)

    italicChanged = pyqtSignal(bool)

    underlineChanged = pyqtSignal(bool)

    pixelSizeChanged = pyqtSignal(int)

    pointSizeChanged = pyqtSignal(float)

    isAnchorChanged = pyqtSignal(bool)

    anchorHrefChanged = pyqtSignal(text_type)

    foregroundColorChanged = pyqtSignal(QColor)

    backgroundColorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super(CharFormatProxy, self).__init__(parent)
        self._charFormat = QTextCharFormat()
        self._fontFamily = None
        self._bold = False
        self._italic = False
        self._underline = False
        self._pixelSize = -1
        self._pointSize = -1.0
        self._isAnchor = False
        self._anchorHref = ''
        self._foregroundColor = None
        self._backgroundColor = None
        self._blockDiffEmitting = False

    def getCharFormat(self):
        return self._charFormat

    @pyqtSlot(QTextCharFormat)
    def setCharFormat(self, charFormat):
        oldCharFormat = self._charFormat
        if charFormat == oldCharFormat:
            return
        self._charFormat = charFormat

        self.updateCharFormat(self._charFormat)
        self.charFormatChanged.emit(charFormat)

    charFormat = pyqtProperty(QTextCharFormat, getCharFormat, setCharFormat)

    @pyqtSlot(QTextCharFormat)
    def updateCharFormat(self, charFormat):

        family = charFormat.fontFamily() if charFormat.fontFamily() else QFontInfo(charFormat.font()).family()
        self.setFontFamily(family)
        self.setBold(int(charFormat.fontWeight()) > 50)
        self.setItalic(charFormat.fontItalic())
        self.setUnderline(charFormat.fontUnderline())
        fontSize = charFormat.fontPointSize() if charFormat.fontPointSize() else charFormat.font().pointSizeF()
        self.setPointSize(fontSize)
        self.setAnchorHref(charFormat.anchorHref())
        self.setForegroundColor(charFormat.foreground().color())

    @pyqtSlot(QTextCharFormat)
    def updateCharFormatWithoutDiffs(self, charFormat):
        self._blockDiffEmitting = True
        self.updateCharFormat(charFormat)
        self._blockDiffEmitting = False

    def getFontFamily(self):
        return self._fontFamily

    @pyqtSlot(text_type)
    def setFontFamily(self, family):
        if self.getFontFamily() == family:
            return
        self._charFormat.setFontFamily(family)
        self._fontFamily = family
        self.fontFamilyChanged.emit(family)
        self.charFormatModified.emit(self._charFormat)
        diff = QTextCharFormat()
        diff.setFontFamily(family)
        self._emitDiff(diff)

    fontFamily = pyqtProperty(text_type, getFontFamily, setFontFamily)

    def getBold(self):
        return self._bold

    @pyqtSlot(bool)
    def setBold(self, bold):
        if self.getBold() == bold:
            return
        boldEnum = QFont.Bold if bold else QFont.Normal
        self._charFormat.setFontWeight(boldEnum)
        self._bold = bold
        self.boldChanged.emit(bold)
        self.charFormatModified.emit(self._charFormat)
        diff = QTextCharFormat()
        diff.setFontWeight(boldEnum)
        self._emitDiff(diff)

    bold = pyqtProperty(bool, getBold, setBold)

    def getItalic(self):
        return self._italic

    @pyqtSlot(bool)
    def setItalic(self, italic):
        if self.getItalic() == italic:
            return
        self._charFormat.setFontItalic(italic)
        self._italic = italic
        self.italicChanged.emit(italic)
        self.charFormatModified.emit(self._charFormat)
        diff = QTextCharFormat()
        diff.setFontItalic(italic)
        self._emitDiff(diff)

    italic = pyqtProperty(bool, getItalic, setItalic)

    def getUnderline(self):
        return self._underline

    @pyqtSlot(bool)
    def setUnderline(self, underline):
        if self.getUnderline() == underline:
            return
        self._charFormat.setFontUnderline(underline)
        self._underline = underline
        self.underlineChanged.emit(underline)
        self.charFormatModified.emit(self._charFormat)
        diff = QTextCharFormat()
        diff.setFontUnderline(underline)
        self._emitDiff(diff)

    underline = pyqtProperty(bool, getUnderline, setUnderline)

    def getPointSize(self):
        return self._pointSize

    @pyqtSlot(float)
    def setPointSize(self, pointSize):
        if self.getPointSize() == pointSize:
            return
        self._charFormat.setFontPointSize(pointSize)
        self._pointSize = pointSize
        self.pointSizeChanged.emit(pointSize)
        self.charFormatModified.emit(self._charFormat)
        diff = QTextCharFormat()
        diff.setFontPointSize(pointSize)
        self._emitDiff(diff)

    pointSize = pyqtProperty(float, getPointSize, setPointSize)


    def getPixelSize(self):
        return self._pixelSize

    def setPixelSize(self, pixelSize):
        if self.getPixelSize() == pixelSize():
            return
        self._charFormat.setFontPixelSize(pixelSize)
        self._pixelSize = pixelSize
        self.pixelSizeChanged.emit(pixelSize)
        self.charFormatModified.emit(self._charFormat)
        diff = QTextCharFormat()
        diff.setFontPixelSize(pixelSize)
        self._emitDiff(diff)

    pixelSize = pyqtProperty(int, getPixelSize, setPixelSize)

    def anchorHref(self):
        return self._anchorHref

    def setAnchorHref(self, href):
        currentHref = self.anchorHref()
        if currentHref == href:
            return
        self._charFormat.setAnchorHref(href)
        self._anchorHref = href
        self.anchorHrefChanged.emit(href)
        self.charFormatModified.emit(self._charFormat)
        if bool(currentHref) != bool(href):
            self.isAnchorChanged.emit(bool(href))
        diff = QTextCharFormat()
        diff.setAnchorHref(href)
        self._emitDiff(diff)

    def getForegroundColor(self):
        return self._foregroundColor

    def setForegroundColor(self, color):
        if self.getForegroundColor() == color:
            return
        self._charFormat.setForeground(color)
        self._foregroundColor = color
        self.foregroundColorChanged.emit(color)
        self.charFormatModified.emit(self._charFormat)
        diff = QTextCharFormat()
        diff.setForeground(color)
        self._emitDiff(diff)

    def clearFormat(self):
        self.setCharFormat(QTextCharFormat())

    def _emitDiff(self, diff):
        if self._blockDiffEmitting:
            return
        self.charFormatDiffChanged.emit(diff)

    def _charFormatsAreEqual(self, left, right):
        if left.font() != right.font():
            return False
        if left.isAnchor() != right.isAnchor():
            return False
        if left.anchorHref() != right.anchorHref():
            return False
        if left.foreground() != right.foreground():
            return False
        return True