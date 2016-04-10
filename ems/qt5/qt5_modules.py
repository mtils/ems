
import ems.qt

from PyQt5 import QtCore

ems.qt.QtCore = QtCore

try:
    from PyQt5 import QtGui
    ems.qt.QtGui = QtGui
except ImportError:
    pass

try:
    from PyQt5 import QtWidgets
    ems.qt.QtWidgets = QtWidgets
except ImportError:
    pass

try:
    from PyQt5 import QtQuick
    ems.qt.QtQuick = QtQuick
except ImportError:
    pass

try:
    from PyQt5 import QtPrintSupport
    ems.qt.QtPrintSupport = QtPrintSupport
except ImportError:
    pass