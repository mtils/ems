from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QPoint,QRect,QVariant, Qt

from ems.qt4.util import variant_to_pyobject

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class ImgRepeatEditor(QtGui.QWidget):

    editingFinished = QtCore.pyqtSignal()

    def __init__(self, delegate, parent = None, reversedMode=False):
        super(ImgRepeatEditor, self).__init__(parent)
        self.reversedMode = reversedMode
        self._value = 0
        self._delegate = delegate
        self.setMouseTracking(True)
        self.setAutoFillBackground(True)

    def setValue(self, starRating):
        self._value = starRating

    def getValue(self):
        if not self.reversedMode:
            return self._value
        return self._delegate.maxValue + 1 - self._value

    def sizeHint(self):
        return self._delegate.sizeHint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self._delegate.paintDisplay(self._value,painter, self.rect(), self.palette(),
                ImgRepeatDelegate.Editable)

    def mouseMoveEvent(self, event):
        value = self.valueAtPosition(event.x())

        if value != self._value and value != -1:
            self._value = value
            self.update()

    def mouseReleaseEvent(self, event):
        self.editingFinished.emit()

    def valueAtPosition(self, x):
        imgwidth = self._delegate.currentWidth // self._delegate.maxValue
        value = (x + imgwidth / 2) // imgwidth
        if 0 <= value <= self._delegate.maxValue:
            return value
        return -1


class ImgRepeatDelegate(QtGui.QStyledItemDelegate):
    # enum EditMode
    Editable, ReadOnly = range(2)
    
    def __init__(self, activeImage, maxValue=5, hMargin=1, initialImgSize=20,
                  reversedMode=False, parent=None):
        super(ImgRepeatDelegate, self).__init__(parent)
        self.activeImage = activeImage
        self.maxValue = maxValue
        self.hMargin = hMargin
        self.initialImgSize = initialImgSize
        self.currentWidth = 0
        self.reversedMode = reversedMode

    def getActiveImage(self):
        return self.__activeImage

    def getMaxValue(self):
        return self.__maxValue

    def getHMargin(self):
        return self.__hMargin

    def getInitialImgSize(self):
        return self.__initialImgSize

    def setActiveImage(self, value):
        self.__activeImage = value

    def setMaxValue(self, value):
        self.__maxValue = value

    def setHMargin(self, value):
        self.__hMargin = value

    def setInitialImgSize(self, value):
        self.__initialImgSize = value

    def delActiveImage(self):
        del self.__activeImage

    def delMaxValue(self):
        del self.__maxValue

    def delHMargin(self):
        del self.__hMargin

    def delInitialImgSize(self):
        del self.__initialImgSize
    
    def paint(self, painter, option, index):
        value = index.data()
        if isinstance(value, QVariant) and value.typeName() in ('int','float'):
            value = value.toInt()[0]
        if isinstance(value,(int,float)):
            if option.state & QtGui.QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
            self.paintDisplay(value, painter, option.rect, option.palette,
                    ImgRepeatDelegate.ReadOnly)
        else:
            super(ImgRepeatDelegate, self).paint(painter, option, index)
            
            
    def paintDisplay(self, value, painter, rect, palette, editMode):
        painter.save()

        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtCore.Qt.NoPen)

        if editMode == ImgRepeatDelegate.Editable:
            painter.setBrush(palette.highlight())
        else:
            painter.setBrush(palette.foreground())
        
        hMargin = self.__hMargin
        doubleMarginH = hMargin + hMargin
        self.currentWidth = rect.width()
        imgWidth = (rect.width()) / self.__maxValue - (doubleMarginH)
        try:
            imgRatio = float(self.__activeImage.height())/float(self.__activeImage.width())
        except ZeroDivisionError:
            imgRatio = 0
        imageHeight = imgWidth * imgRatio
        maxHeight = rect.height() - doubleMarginH
        
        if imageHeight > maxHeight:
            oldImgWidth = imgWidth
            imageHeight = maxHeight
            imgWidth = imageHeight / imgRatio
            hMargin = (oldImgWidth - imgWidth) / 2
            doubleMarginH = hMargin + hMargin
        else: 
            pass
        marginV = (rect.height() - imageHeight) / 2
        
        cumulativeOffset = 0
        
        top = rect.top() + marginV
        bottom = top + imageHeight
        if self.reversedMode and editMode != self.Editable:
            value = self.__maxValue + 1 - value
        for i in range(self.__maxValue):
            if i < value:
                leftOffset = rect.left() + cumulativeOffset + hMargin
                rightOffset = leftOffset + imgWidth + hMargin
                trgRect = QRect(QPoint(leftOffset,top),
                                QPoint(rightOffset,bottom))
                painter.drawImage(trgRect,self.__activeImage,self.__activeImage.rect())
            elif editMode == ImgRepeatDelegate.Editable:
                pass
            cumulativeOffset += imgWidth + doubleMarginH

        painter.restore()
    
    def defaultSizeHint(self):
        return (self.__initialImgSize + (self.__hMargin * 2)) *\
                     QtCore.QSize(self.__maxValue, 1)

    def sizeHint(self, option, index):
        value = index.data()
        if isinstance(value, QVariant) and value.typeName() in ('int','float','double'):
            value = value.toInt()[0]
        if isinstance(value, (int,float)):
            return self.defaultSizeHint()
        else:
            return super(ImgRepeatDelegate, self).sizeHint(option, index)

    def createEditor(self, parent, option, index):
        value = index.data()
        if isinstance(value, QVariant) and value.typeName() in ('int','float','double'):
            value = value.toInt()[0]
        if isinstance(value, (int,float)):
            editor = ImgRepeatEditor(self,parent,reversedMode=self.reversedMode)
            editor.editingFinished.connect(self.commitAndCloseEditor)
            return editor
        else:
            return super(ImgRepeatDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        value = index.data()
        if isinstance(value, QVariant) and value.typeName() in ('int','float','double'):
            value = value.toInt()[0]
        if isinstance(value, (int,float)):
            editor.setValue(value)
        else:
            super(ImgRepeatDelegate, self).setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        value = index.data()
        if isinstance(value, QVariant) and value.typeName() in ('int','float','double'):
            value = value.toInt()[0]
        if isinstance(value, (int,float)):
            model.setData(index, editor.getValue())
        else:
            super(ImgRepeatDelegate, self).setModelData(editor, model, index)

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)

    activeImage = property(getActiveImage, setActiveImage, delActiveImage, "activeImage's docstring")
    maxValue = property(getMaxValue, setMaxValue, delMaxValue, "maxValue's docstring")
    hMargin = property(getHMargin, setHMargin, delHMargin, "hMargin's docstring")
    initialImgSize = property(getInitialImgSize, setInitialImgSize, delInitialImgSize, "initialImgSize's docstring")

class UnitDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, prefix="",suffix="", numberfmt=None, parent=None):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.prefix = prefix
        self.suffix = suffix
        self.thousandsSeparator = '.'
        self.decimalPoint = ','
        self._lastValue = ''
        
        if isinstance(numberfmt, basestring):
            if numberfmt.startswith('{') or numberfmt.startswith('%'):
                raise TypeError("I need clean numberformats, not {0}".format(numberfmt))
            else:
                self.numberformat = numberfmt
        else:
            self.numberformat = ""
            
        
        if self.numberformat:
            self._pyNumberFormat = "{0:" + self.numberformat + "}"
        else:
            self._pyNumberFormat = "{0}"
    
    def getString(self, value):
#        print self.numberformat, value
        strValue = self._pyNumberFormat.format((value)).replace('.',self.decimalPoint)
#        print "'{0}'".format(strValue)
        string = unicode(self.prefix+strValue+self.suffix)
        return string
    
    def paint(self, painter, option, index):
        value = variant_to_pyobject(index.data())
        self._lastValue = value
        if isinstance(value,(int,float)):
            options = QtGui.QStyleOptionViewItemV4(option)
            self.initStyleOption(options, index)
            options.displayAlignment = Qt.AlignRight | Qt.AlignVCenter
            
            style = QtGui.QApplication.style() if options.widget is None \
                else options.widget.style()
            
            string = self.getString(value)
#            print "'{0}'".format(string)
            options.text = QtCore.QString.fromUtf8(string)
            style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter)
            
            return None
        
        
        return super(UnitDelegate, self).paint(painter, option, index)
    
    def sizeHint(self, option, index):
        #print "sizeHint"
        #print option.text
        value = variant_to_pyobject(index.data())
        if isinstance(value,(int,float)):
            options = QtGui.QStyleOptionViewItemV4(option)
            self.initStyleOption(options, index)
            options.displayAlignment = Qt.AlignRight | Qt.AlignVCenter
            options.text = QtCore.QString.fromUtf8(self.getString(value))
            width = options.fontMetrics.width(options.text) + 6
            return QtCore.QSize(width, options.rect.height())
        return QtGui.QStyledItemDelegate.sizeHint(self, option, index)
