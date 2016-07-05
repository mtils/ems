
from ems.qt import QtWidgets, QtGui, QtCore

QSlider = QtWidgets.QSlider
pyqtSignal = QtCore.pyqtSignal
pyqtProperty = QtCore.pyqtProperty
pyqtSlot = QtCore.pyqtSlot

class OneOfAListSlider(QSlider):

    listValueChanged = pyqtSignal(int)

    valueListChanged = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(OneOfAListSlider, self).__init__(parent)
        self._valueList = None
        self.valueChanged.connect(self._updateListValue)
        self.setSingleStep(1)
        self.setValueList((1,2,3,4,5,6,7,8,9,10))

    def getValueList(self):
        return self._valueList

    @pyqtSlot(tuple)
    def setValueList(self, valueList):
        if self._valueList == valueList:
            return
        self._valueList = tuple(valueList)
        self.setRange(0, len(self._valueList)-1)
        self.valueListChanged.emit(self._valueList)

    valueList = pyqtProperty(tuple, getValueList, setValueList)

    def getListValue(self):
        return self._valueList[self.value()]

    def setListValue(self, listValue):
        if listValue == self.getListValue():
            return
        self.setValue(self._valueList.index(listValue))

    def moveHandleRelative(self, upOrDown):
        """
        Moves relative up=1, down=-1
        """
        self.setValue(self.value()+upOrDown)

    def _updateListValue(self, value):
        self.listValueChanged.emit(self._valueList[value])