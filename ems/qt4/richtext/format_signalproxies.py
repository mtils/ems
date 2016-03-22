
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal, QString, pyqtProperty
from PyQt4.QtGui import QTextFormat, QTextCharFormat, QFont, QFontInfo
from PyQt4.QtGui import QBrush, QColor

class TextFormatSignalProxy(QObject):
    pass

class CharFormatSignalProxy(QObject):

    charFormatChanged = pyqtSignal(QTextCharFormat)

    fontChanged = pyqtSignal(QFont)

    fontFamilyChanged = pyqtSignal(QString)

    boldChanged = pyqtSignal(bool)

    italicChanged = pyqtSignal(bool)

    underlineChanged = pyqtSignal(bool)

    pixelSizeChanged = pyqtSignal(int)

    pointSizeChanged = pyqtSignal(int)

    isAnchorChanged = pyqtSignal(bool)

    anchorHrefChanged = pyqtSignal(QString)

    foregroundChanged = pyqtSignal(QBrush)

    foregroundColorChanged = pyqtSignal(QColor)

    backgroundChanged = pyqtSignal(QBrush)

    backgroundColorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super(CharFormatSignalProxy, self).__init__(parent)
        self._charFormat = QTextCharFormat()
        self._font = self._charFormat.font()
        self._fontFamily = QFontInfo(self._font).family()
        self._bold = self._font.bold()
        self._italic = self._font.italic()
        self._underline = self._font.underline()
        self._pixelSize = self._font.pixelSize()
        self._pointSize = self._font.pointSize()
        self._isAnchor = False
        self._anchor = ''
        self._foreground = self._charFormat.foreground()
        self._foregroundColor = self._charFormat.foreground().color()
        self._background = self._charFormat.background()
        self._backgroundColor = self._charFormat.background().color()

    def getCharFormat(self):
        return self._charFormat

    @pyqtSlot(QTextCharFormat)
    def setCharFormat(self, charFormat):
        oldCharFormat = self._charFormat
        print('setCharFormat', charFormat, oldCharFormat)
        if self._charFormatsAreEqual(oldCharFormat, charFormat):
            print('equal')
            return
        self._charFormat = charFormat
        self.charFormatChanged.emit(charFormat)
        self._replaceFont(oldCharFormat.font(), charFormat.font())

        if oldCharFormat.anchorHref() != charFormat.anchorHref():
            self.anchorHrefChanged.emit(charFormat.anchorHref())

        if bool(oldCharFormat.anchorHref()) != bool(charFormat.anchorHref()):
            self.isAnchorChanged.emit(bool(oldCharFormat.anchorHref()))

        if oldCharFormat.foreground() != charFormat.foreground():
            self.foregroundChanged.emit(charFormat.foreground())

        if oldCharFormat.foreground().color() != charFormat.foreground().color():
            self.foregroundColorChanged.emit(charFormat.foreground().color())

    charFormat = pyqtProperty(QTextCharFormat, getCharFormat, setCharFormat)

    def getFont(self):
        return self._charFormat.font()

    @pyqtSlot(QFont)
    def setFont(self, newFont):
        self._replaceFont(self._charFormat.font(), newFont)

    font = pyqtProperty(QFont, getFont, setFont)

    def _replaceFont(self, oldFont, newFont):
        if oldFont == newFont:
            return

        self._charFormat.setFont(newFont)
        self.fontChanged.emit(newFont)

        newFontFamily = QFontInfo(newFont).family()

        if newFontFamily != QFontInfo(oldFont).family():
            self.fontFamilyChanged.emit(newFontFamily)

        if newFont.bold() != oldFont.bold():
            self.boldChanged.emit(newFont.bold())

        if newFont.italic() != oldFont.italic():
            self.italicChanged.emit(newFont.italic())

        if newFont.underline() != oldFont.underline():
            self.underlineChanged.emit(newFont.underline())

        if newFont.pointSize() != oldFont.pointSize():
            self.pointSizeChanged.emit(newFont.pointSize())

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

    def anchorHref(self):
        return self._charFormat.anchorHref()

    def setAnchorHref(self, href):
        currentHref = self.anchorHref()
        if currentHref == href:
            return
        self._charFormat.setAnchorHref(href)
        self.anchorHrefChanged.emit(href)
        if bool(currentHref) != bool(href):
            self.isAnchorChanged.emit(bool(href))

    def getForeground(self):
        return self._charFormat.foreground()

    @pyqtSlot(QBrush)
    def setForeground(self, foreground):
        oldForeground = self.getForeground()
        if self.getForeground() == foreground:
            return
        self._charFormat.setForeground(foreground)
        self.foregroundChanged.emit(foreground)
        if oldForeground.color() != foreground.color():
            self.foregroundColorChanged.emit(foreground.color())

    foreground = pyqtProperty(QBrush, getForeground, setForeground)

    def getForegroundColor(self):
        return self._charFormat.foreground().color()

    def setForegroundColor(self, color):
        if self.getForegroundColor() == color:
            return
        self._charFormat.foreground().setColor(color)
        self.foregroundColorChanged.emit(color)

    def _charFormatsAreEqual(self, left, right):
        if left.font() != right.font():
            return False
        if left.isAnchor() != right.isAnchor():
            return False
        if left.anchorHref() != right.anchorHref():
            return False
        return True