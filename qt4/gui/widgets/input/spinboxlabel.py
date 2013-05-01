import re

from PyQt4.QtCore import pyqtSignal, QString, Qt, QSize
from PyQt4.QtGui import QLineEdit, QIntValidator, QFontMetrics, QApplication,\
    QStyleOption

class SpinBoxLabel(QLineEdit):

    valueChanged = pyqtSignal([int],['QString'])

    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        self._minimum = 0
        self._maximum = 100
        self._singleStep = 1
        self._specialValueText = ''
        self._value = -1
        self._prefix = ''
        self._suffix = ''
        self.setValidator(QIntValidator(self._minimum, self._maximum, self))
        self.textChanged.connect(self._onTextChanged)
        self.blockSignals(True)
        self.setValue(0)
        self.blockSignals(False)
        self.setAlignment(Qt.AlignRight)

    def clear(self):
        self.setText(QString.fromUtf8(u'%1%2%3').arg(self._prefix,'', self._suffix))

    def stepDown(self):
        self.setValue(self._value - self._singleStep)

    def stepUp(self):
        self.setValue(self._value + self._singleStep)

    def specialValueText(self):
        return self._specialValueText

    def setSpecialValueText(self, text):
        self._specialValueText = text

    def stepBy(self, steps):
        self.setValue(self._value + (steps * self._singleStep))

    def singleStep(self):
        return self._singleStep
    
    def setSingleStep(self, singleStep):
        self._singleStep = singleStep

    def value(self):
        return self._value

    def setValue(self, value):
        if value == self._value:
            return
        if value > self._maximum or value < self._minimum:
            return
        self._value = value
        self.valueChanged[int].emit(self._value)
        self.valueChanged['QString'].emit(QString(self._value))
        self._updateText()

    def _updateText(self):
        valueText = u'{0}{1}{2}'.format(self._prefix, self._value, self._suffix)
        self.setText(QString.fromUtf8(valueText))

    def minimum(self):
        return self._minimum

    def setMinimum(self, minimum):
        self._minimum = minimum
        self.validator().setBottom(minimum)

    def maximum(self):
        return self._maximum

    def setMaximum(self, maximum):
        self._maximum = maximum
        self.validator().setTop(maximum)
    
    def setRange(self, minimum, maximum):
        self._minimum = minimum
        self._maximum = maximum
        self.validator().setRange(minimum, maximum)

    def prefix(self):
        return self._prefix

    def setPrefix(self, prefix):
        if self._prefix == prefix:
            return
        self._prefix = prefix
        self._updateText()

    def suffix(self):
        return self._suffix

    def setSuffix(self, suffix):
        if self._suffix == suffix:
            return
        self._suffix = suffix
        self._updateText()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            self.stepBy(self._singleStep)
        elif event.key() == Qt.Key_Down:
            self.stepBy(0-self._singleStep)
        elif event.key() == Qt.Key_PageUp:
            self.stepBy(self._singleStep*10)
        elif event.key() == Qt.Key_PageDown:
            self.stepBy(0-self._singleStep*10)
        else:
            QLineEdit.keyPressEvent(self, event)
    
    def _onTextChanged(self, text):
        text = unicode(text)
        textLength = len(text)
        number = text[len(self._prefix):len(self._prefix)+textLength-len(self._suffix)]
        maxLength = len(unicode(self._maximum))
        #res = re.search("[\d-]\{1,{0}\}[\W]\{0,2\}[a-zA-Z0-9]\{0,6\}".format(maxLength), text)
        res = re.search('(\+|-)?([0-9]+)', text)
        match = ''
        cursorPos = self.cursorPosition()
        if res is not None:
            match = unicode(res.group(0))
        if match != '':
            self.setValue(int(match))
            self.setCursorPosition(cursorPos)

    def minimumSizeHint(self):
        originalSizeHint = QLineEdit.minimumSizeHint(self)

        # + or - can be prior number
        longestStr = unicode(self._prefix) + unicode(str(self._maximum)+' ') + unicode(self._suffix)
        
        fm = QFontMetrics(self.font())
        width = fm.width(QString.fromUtf8(longestStr))
        charWidth = fm.width('8')
        margin = originalSizeHint.width()-charWidth
        width += margin
        return QSize(width, originalSizeHint.height())
    
    def sizeHint(self):
        return self.minimumSizeHint()