
import ems.qt

from PyQt4 import QtCore

ems.qt.QtCore = QtCore

try:
    from PyQt4 import QtGui
    ems.qt.QtGui = QtGui
    ems.qt.QtWidgets = QtGui
    ems.qt.QtPrintSupport = QtGui
except ImportError:
    pass

