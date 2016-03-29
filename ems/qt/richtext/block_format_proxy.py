
from ems.qt import QtCore
from ems.qt import QtGui

QObject = QtCore.QObject
pyqtSlot = QtCore.pyqtSlot
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
Qt = QtCore.Qt
QTextBlockFormat = QtGui.QTextBlockFormat

class BlockFormatProxy(QObject):
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
        super(BlockFormatProxy, self).__init__(parent)
        self._alignment = Qt.AlignLeft | Qt.AlignTop
        self._blockFormat = QTextBlockFormat()
        self._blockFormat.setAlignment(self._alignment)
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