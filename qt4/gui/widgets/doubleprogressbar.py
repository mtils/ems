#coding=utf-8

from PyQt4.QtCore import pyqtSignal, pyqtSlot, QString
from PyQt4.QtGui import QProgressBar

class DoubleProgressBar(QProgressBar):
    
    __multiplicator = 10
    
    _decimals = 1
    
    valueChanged = pyqtSignal(float)
    
    def __init__(self, decimals=None, parent=None):
        QProgressBar.__init__(self, parent)
        if decimals is None:
            decimals = 1
        self.setDecimals(decimals)
        self.setMinimum(0.0)
        self.setMaximum(1.0)
    
    def text(self):
        if self.value() < self.minimum():
            return QString()
        formatString = "{0:." + str(self._decimals) + "f}"
        return QString(self.format().replace('%v',formatString.format(self.value())))
    
    def minimum(self):
        return float(QProgressBar.minimum(self))/self.__multiplicator
    
    @pyqtSlot(float)
    def setMinimum(self, minimum):
        QProgressBar.setMinimum(self, int(minimum*self.__multiplicator))
    
    def maximum(self):
        return float(QProgressBar.maximum(self))/self.__multiplicator
    
    @pyqtSlot(float)
    def setMaximum(self, maximum):
        QProgressBar.setMaximum(self, int(maximum*self.__multiplicator))
       
    def value(self):
        return float(QProgressBar.value(self))/self.__multiplicator
    
    @pyqtSlot(float)
    def setValue(self, value):
        if value == self.value():
            return
        QProgressBar.setValue(self, int(value*self.__multiplicator))
        self.valueChanged.emit(value)
    
    def decimals(self):
        return self._decimals
    
    def setDecimals(self, decimals):
        self._decimals = decimals
        self.__multiplicator = 10**decimals


if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import QApplication
    app = QApplication([])
    bar = DoubleProgressBar()
    bar.setFormat(u'%v m²')
    #bar.setMaximum(2.0)
    bar.setValue(0.7)
    bar.show()
    
    
    sys.exit(app.exec_())