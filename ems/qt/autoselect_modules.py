
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
    # First try to get an environment variable
    QT_RC_MAJOR_VERSION = int(QT_API_ENV)
except (ValueError, TypeError):
    # No env, look for already imported modules
    if 'PyQt5' in sys.modules:
        QT_RC_MAJOR_VERSION = 5
    elif 'PyQt4' in sys.modules:
        QT_RC_MAJOR_VERSION = 4
    else:
        # Try an import
        try:
            from PyQt5 import QtCore
            QT_RC_MAJOR_VERSION = 5
        except ImportError:
            try:
                from PyQt4 import QtCore
                QT_RC_MAJOR_VERSION = 4
            except ImportError:
                raise ImportError('No PyQt installation found')


if QT_RC_MAJOR_VERSION == 4:
    import ems.qt4.qt4_modules

elif QT_RC_MAJOR_VERSION == 5:
    import ems.qt5.qt5_modules
