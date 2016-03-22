
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal, QString, pyqtProperty
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTextFormat, QTextCharFormat, QFont, QFontInfo
from PyQt4.QtGui import QBrush, QColor, QTextBlockFormat

class TextFormatSignalProxy(QObject):
    pass

class BlockFormatSignalProxy(QObject):
    '''
    CAUTION: all alignment methods are exclusive. A call to setAlignLeft(False)
    will be ignored, only setAlignLeft() and setAlignLeft(True) will result in
    any change. This makes it easiert to connect to single buttons.
    The question is what should happen if you set alignLeft to False? The
    opposite Qt.AlignRight? This would lead to clicking on the justify button,
    setAlignJustify(True) would be triggered, than the left button would be
    unchecked and it would switch to Qt.AlignRight. So this is the reason for
    the strange API.
    '''

    blockFormatChanged = pyqtSignal(QTextBlockFormat)

    blockFormatModified = pyqtSignal(QTextBlockFormat)

    alignmentChanged = pyqtSignal(Qt.Alignment)

    alignLeftChanged = pyqtSignal(bool)

    alignRightChanged = pyqtSignal(bool)

    alignCenterChanged = pyqtSignal(bool)

    alignJustifyChanged = pyqtSignal(bool)

    alignTopChanged = pyqtSignal(bool)

    alignBottomChanged = pyqtSignal(bool)

    alignMiddleChanged = pyqtSignal(bool)

    leftMarginChanged = pyqtSignal(float)

    rightMarginChanged = pyqtSignal(float)

    topMarginChanged = pyqtSignal(float)

    bottomMarginChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super(BlockFormatSignalProxy, self).__init__(parent)
        self._blockFormat = None
        self._alignment = Qt.AlignLeft | Qt.AlignTop
        self._alignLeft = True
        self._alignRight = True
        self._alignCenter = False
        self._alignJustify = False
        self._alignTop = True
        self._alignBottom = False
        self._alignMiddle = False
        self._leftMargin = 0.0
        self._rightMargin = 0.0
        self._topMargin = 0.0
        self._bottomMargin = 0.0

    def getBlockFormat(self):
        return self._blockFormat

    def setBlockFormat(self, blockFormat):
        if self._blockFormat == blockFormat:
            return
        self._blockFormat = blockFormat
        self.updateBlockFormat(self._blockFormat)
        self.blockFormatChanged.emit(self._blockFormat)

    blockFormat = pyqtProperty(QTextBlockFormat, getBlockFormat, setBlockFormat)

    @pyqtSlot(QTextBlockFormat)
    def updateBlockFormat(self, blockFormat):

        horizontalAlign = self._horizontalAlignment(blockFormat.alignment())
        verticalAlign = self._verticalAlignment(blockFormat.alignment())

        if horizontalAlign == Qt.AlignLeft:
            self.setAlignLeft()
        elif horizontalAlign == Qt.AlignCenter:
            self.setAlignCenter()
        elif horizontalAlign == Qt.AlignRight:
            self.setAlignRight()
        elif horizontalAlign == Qt.AlignJustify:
            self.setAlignJustify()

        if verticalAlign == Qt.AlignTop:
            self.setAlignTop()
        elif verticalAlign == Qt.AlignVCenter:
            self.setAlignMiddle()
        elif verticalAlign == Qt.AlignBottom:
            self.setAlignBottom()

        self.setLeftMargin(blockFormat.leftMargin())
        self.setRightMargin(blockFormat.rightMargin())
        self.setTopMargin(blockFormat.topMargin())
        self.setBottomMargin(blockFormat.bottomMargin())

    def getAlignment(self):
        return self._blockFormat.alignment()

    alignment = pyqtProperty(Qt.Alignment, getAlignment)

    def getAlignLeft(self):
        return self._alignLeft

    @pyqtSlot()
    @pyqtSlot(bool)
    def setAlignLeft(self, align=True):
        if self.getAlignLeft() or not align:
            return
        verticalAlign = self._verticalAlignment(self.getAlignment())
        alignment = verticalAlign | Qt.AlignLeft

        self._alignLeft = True
        self._blockFormat.setAlignment(alignment)
        self._deactivateHorizontalIfTrue()
        self.alignLeftChanged.emit(True)

        self._emitBlockFormatModified(self._blockFormat)

    alignLeft = pyqtProperty(bool, getAlignLeft, setAlignLeft)

    def getAlignRight(self):
        return self._alignRight

    @pyqtSlot()
    @pyqtSlot(bool)
    def setAlignRight(self, align=True):
        if self.getAlignRight() or not align:
            return
        verticalAlign = self._verticalAlignment(self.getAlignment())
        alignment = verticalAlign | Qt.AlignRight

        self._alignRight = True
        self._blockFormat.setAlignment(alignment)
        self._deactivateHorizontalIfTrue()
        self.alignRightChanged.emit(True)

        self._emitBlockFormatModified(self._blockFormat)

    alignRight = pyqtProperty(bool, getAlignRight, setAlignRight)

    def getAlignCenter(self):
        return self._alignCenter

    @pyqtSlot()
    @pyqtSlot(bool)
    def setAlignCenter(self, align=True):
        if self.getAlignCenter() or not align:
            return
        verticalAlign = self._verticalAlignment(self.getAlignment())
        alignment = verticalAlign | Qt.AlignCenter

        self._alignCenter = True
        self._blockFormat.setAlignment(alignment)
        self._deactivateHorizontalIfTrue()
        self.alignCenterChanged.emit(True)

        self._emitBlockFormatModified(self._blockFormat)

    alignCenter = pyqtProperty(bool, getAlignCenter, setAlignCenter)

    def getAlignJustify(self):
        return self._alignJustify

    @pyqtSlot()
    @pyqtSlot(bool)
    def setAlignJustify(self, align=True):
        if self.getAlignJustify() or not align:
            return
        verticalAlign = self._verticalAlignment(self.getAlignment())
        alignment = verticalAlign | Qt.AlignJustify

        self._alignJustify = True
        self._blockFormat.setAlignment(alignment)
        self._deactivateHorizontalIfTrue()
        self.alignJustifyChanged.emit(True)

        self._emitBlockFormatModified(self._blockFormat)

    alignJustify = pyqtProperty(bool, getAlignJustify, setAlignJustify)

    def getAlignTop(self):
        return self._alignTop

    @pyqtSlot()
    @pyqtSlot(bool)
    def setAlignTop(self, align=True):
        if self.getAlignTop() or not align:
            return
        horizontalAlign = self._horizontalAlignment(self.getAlignment())
        alignment = horizontalAlign | Qt.AlignTop

        self._alignTop = True
        self._blockFormat.setAlignment(alignment)
        self._deactivateVerticalIfTrue()
        self.alignTopChanged.emit(True)

        self._emitBlockFormatModified(self._blockFormat)

    alignTop = pyqtProperty(bool, getAlignTop, setAlignTop)

    def getAlignMiddle(self):
        return self._alignMiddle

    @pyqtSlot()
    @pyqtSlot(bool)
    def setAlignMiddle(self, align=True):
        if self.getAlignMiddle() or not align:
            return
        horizontalAlign = self._horizontalAlignment(self.getAlignment())
        alignment = horizontalAlign | Qt.AlignMiddle

        self._alignMiddle = True
        self._blockFormat.setAlignment(alignment)
        self._deactivateVerticalIfTrue()
        self.alignMiddleChanged.emit(True)

        self._emitBlockFormatModified(self._blockFormat)

    alignMiddle = pyqtProperty(bool, getAlignMiddle, setAlignMiddle)

    def getAlignBottom(self):
        return self._alignBottom

    @pyqtSlot()
    @pyqtSlot(bool)
    def setAlignBottom(self, align=True):
        if self.getAlignBottom() or not align:
            return
        horizontalAlign = self._horizontalAlignment(self.getAlignment())
        alignment = horizontalAlign | Qt.AlignBottom

        self._alignBottom = True
        self._blockFormat.setAlignment(alignment)
        self._deactivateVerticalIfTrue()
        self.alignBottomChanged.emit(True)

        self._emitBlockFormatModified(self._blockFormat)

    alignBottom = pyqtProperty(bool, getAlignBottom, setAlignBottom)

    def getLeftMargin(self):
        return self._leftMargin

    @pyqtSlot(float)
    def setLeftMargin(self, margin):
        if self.getLeftMargin() == margin:
            return
        self._leftMargin = margin
        self._blockFormat.setLeftMargin(margin)
        self.leftMarginChanged.emit(margin)
        self._emitBlockFormatModified(self._blockFormat)

    leftMargin = pyqtProperty(float, getLeftMargin, setLeftMargin)

    def getRightMargin(self):
        return self._rightMargin

    @pyqtSlot(float)
    def setRightMargin(self, margin):
        if self.getRightMargin() == margin:
            return
        self._rightMargin = margin
        self._blockFormat.setRightMargin(margin)
        self.rightMarginChanged.emit(margin)
        self._emitBlockFormatModified(self._blockFormat)

    rightMargin = pyqtProperty(float, getRightMargin, setRightMargin)

    def getTopMargin(self):
        return self._topMargin

    @pyqtSlot(float)
    def setTopMargin(self, margin):
        if self.getTopMargin() == margin:
            return
        self._topMargin = margin
        self._blockFormat.setTopMargin(margin)
        self.topMarginChanged.emit(margin)
        self._emitBlockFormatModified(self._blockFormat)

    topMargin = pyqtProperty(float, getTopMargin, setTopMargin)

    def getBottomMargin(self):
        return self._bottomMargin

    @pyqtSlot(float)
    def setBottomMargin(self, margin):
        if self.getBottomMargin() == margin:
            return
        self._bottomMargin = margin
        self._blockFormat.setBottomMargin(margin)
        self.bottomMarginChanged.emit(margin)
        self._emitBlockFormatModified(self._blockFormat)

    bottomMargin = pyqtProperty(float, getBottomMargin, setBottomMargin)

    def _horizontalAlignment(self, alignment):
        if alignment & Qt.AlignLeft:
            return Qt.AlignLeft
        if alignment & Qt.AlignCenter:
            return Qt.AlignCenter
        if alignment & Qt.AlignJustify:
            return Qt.AlignJustify
        if alignment & Qt.AlignRight:
            return Qt.AlignRight
        return Qt.AlignLeft

    def _verticalAlignment(self, alignment):
        if alignment & Qt.AlignTop:
            return Qt.AlignTop
        if alignment & Qt.AlignVCenter:
            return Qt.AlignVCenter
        if alignment & Qt.AlignBottom:
            return Qt.AlignBottom
        return Qt.AlignTop

    def _emitBlockFormatModified(self, blockFormat):
        self.blockFormatModified.emit(blockFormat)

    def _deactivateHorizontalIfTrue(self):
        self._deactivateIfTrue(['Left', 'Center', 'Right', 'Justify'])

    def _deactivateVerticalIfTrue(self):
        self._deactivateIfTrue(['Top', 'Middle', 'Bottom'])

    def _deactivateIfTrue(self, directions):
        for group in directions:
            attribute = '_align{}'.format(group)
            if not getattr(self, attribute):
                continue
            setattr(self, attribute, False)
            getattr(self, 'align{}Changed'.format(group)).emit(False)

class CharFormatSignalProxy(QObject):

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

    fontFamilyChanged = pyqtSignal(QString)

    boldChanged = pyqtSignal(bool)

    italicChanged = pyqtSignal(bool)

    underlineChanged = pyqtSignal(bool)

    pixelSizeChanged = pyqtSignal(int)

    pointSizeChanged = pyqtSignal(float)

    isAnchorChanged = pyqtSignal(bool)

    anchorHrefChanged = pyqtSignal(QString)

    foregroundChanged = pyqtSignal(QBrush)

    foregroundColorChanged = pyqtSignal(QColor)

    backgroundChanged = pyqtSignal(QBrush)

    backgroundColorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super(CharFormatSignalProxy, self).__init__(parent)
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

    @pyqtSlot(QString)
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

    fontFamily = pyqtProperty(QString, getFontFamily, setFontFamily)

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