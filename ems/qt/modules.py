
import os, sys

from ems import constants

# Available APIs.
QT_API_PYQT = 'PyQt4'       # API is not set here; Python 2.x default is V 1
QT_API_PYQTv2 = 'PyQt4v2'   # forced to Version 2 API
QT_API_PYSIDE = 'PySide'    # only supports Version 2 API
QT_API_PYQT5 = 'PyQt5'      # use PyQt5 API; Version 2 with module shim
QT_API_PYSIDE2 = 'PySide2'  # Version 2 API with module shim

ETS = dict(pyqt=(QT_API_PYQTv2, 4), pyside=(QT_API_PYSIDE, 4),
           pyqt5=(QT_API_PYQT5, 5), pyside2=(QT_API_PYSIDE2, 5))
# ETS is a dict of env variable to (QT_API, QT_MAJOR_VERSION)
# If the ETS QT_API environment variable is set, use it, but only
# if the varible if of the same major QT version.  Note that
# ETS requires the version 2 of PyQt4, which is not the platform
# default for Python 2.x.

QT_API_ENV = os.environ.get('QT_API')

try:
    QT_RC_MAJOR_VERSION = int(QT_API_ENV)
except (ValueError, TypeError):
    if constants['qtVersion'] == 5:
        QT_RC_MAJOR_VERSION = 5
    elif constants['qtVersion'] == 4:
        QT_RC_MAJOR_VERSION = 4
    else:
        # A different backend was specified, but we still got here because a Qt
        # related file was imported. This is allowed, so lets try and guess
        # what we should be using.
        if "PyQt4" in sys.modules or "PySide" in sys.modules:
            # PyQt4 or PySide is actually used.
            QT_RC_MAJOR_VERSION = 4
        else:
            # This is a fallback: PyQt5
            QT_RC_MAJOR_VERSION = 5

if QT_RC_MAJOR_VERSION == 4:
    from PyQt4 import QtCore
    from PyQt4 import QtGui
    from PyQt4 import QtDeclarative
    QtWidgets = QtGui

elif QT_RC_MAJOR_VERSION == 5:
    from PyQt5 import QtCore
    from PyQt5 import QtGui
    from PyQt5 import QtWidgets

print(QT_RC_MAJOR_VERSION, QtCore)