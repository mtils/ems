
import os.path

from ems.qt import QtCore
from ems.qt import QtWidgets

QTimer = QtCore.QTimer
Qt = QtCore.Qt
QApplication = QtWidgets.QApplication
QAction = QtWidgets.QAction
#from ems.qt.QtCore import QTimer, Qt
#from ems.qt.QtWidgets import QApplication, QAction

from ems.util import platformName
from ems.app import App

class MainApplication(QApplication, App):
    '''
    classdocs
    '''

    def __init__(self, argv, appPath=None):
        '''
        Constructor
        '''
        try:
            QApplication.__init__(self, argv)
        except TypeError:
            pass
        App.__init__(self, argv, appPath)

        self._services = {}
        self._serviceTimers = {}
        self._standardActions = {}
        self._widgetController = None

        if appPath is None:
            self.appPath = os.path.abspath(os.path.dirname(argv[0]))
        else:
            self.appPath = appPath

    def widgetController(self):
        return self._widgetController

    def setWidgetController(self, controller):
        if not callable(controller):
            raise TypeError("Widget Controller has to be callable")
        self._widgetController = controller

    def showWidget(self, widget):
        if self._widgetController:
            self._widgetController(widget)
        else:
            widget.setWindowFlags(Qt.Dialog)
            widget.show()

    def mainWindow(self):

        for widget in self.topLevelWidgets():
            if widget.inherits('QMainWindow'):
                return widget

        return None

    def getStandardAction(self, name):
        action = QAction(self)
        if name in self._standardActions:
            action.setCheckable(self._standardActions[name].isCheckable())
            action.setAutoRepeat(self._standardActions[name].autoRepeat())
            action.setData(self._standardActions[name].data())
            action.setChecked(self._standardActions[name].isChecked())
            action.setEnabled(self._standardActions[name].isEnabled())
            action.setFont(self._standardActions[name].font())
            action.setIcon(self._standardActions[name].icon())
            action.setIconText(self._standardActions[name].iconText())
            action.setIconVisibleInMenu(self._standardActions[name].isIconVisibleInMenu())
            action.setMenuRole(self._standardActions[name].menuRole())
            action.setObjectName(self._standardActions[name].objectName())
            action.setPriority(self._standardActions[name].priority())
            action.setShortcut(self._standardActions[name].shortcut())
            action.setShortcutContext(self._standardActions[name].shortcutContext())
            action.setSoftKeyRole(self._standardActions[name].softKeyRole())
            action.setStatusTip(self._standardActions[name].statusTip())
            action.setText(self._standardActions[name].text())
            action.setToolTip(self._standardActions[name].toolTip())
            action.setVisible(self._standardActions[name].isVisible())
            action.setWhatsThis(self._standardActions[name].whatsThis())
        return action

    def start(self, path, argv):
        App.start(self, path, argv)
        return QApplication.exec_()

    def setStandardAction(self, name, action):
        self._standardActions[name] = action

    def getRelativePath(self, path):
        rPath = path.replace(self.appPath, "")
        if rPath.startswith(os.path.sep):
            return rPath[1:]
        return rPath

    def getAbsolutePath(self, path):
        if os.path.isabs(path):
            return path
        if not path.startswith(os.path.sep):
            return os.path.join(self.appPath, path)
        return path

    def platform(self):
        return platformName()

    def _startOrCreateTimer(self, serviceName):
        if self._services[serviceName].hasOwnTimer():
            return
        if not self._serviceTimers.has_key(serviceName):
            self._serviceTimers[serviceName] = QTimer()
            self._serviceTimers[serviceName].timeout.connect(self._services[serviceName].trigger)

        self._serviceTimers[serviceName].start(self._services[serviceName].pollingInterval())

    def addService(self, name, service):
        if self._services.has_key(name):
            raise AttributeError("The service with the name '{0}' already exists".format(name))
        self._services[name] = service

        if self._services[name].isAutoStartEnabled():
            self.startService(name)

    def removeService(self, name):
        if not self._services.has_key(name):
            raise AttributeError("The service with the name '{0}' does not exist".format(name))
        self._services[name].stop()
        self._services[name].deleteLater()

    def startService(self, name):
        if not self._services.has_key(name):
            raise AttributeError("The service with the name '{0}' does not exist".format(name))
        self._services[name].start()
        self._startOrCreateTimer(name)

    def services(self):
        return self._services.values()

    def stopService(self, name):
        if not self._services.has_key(name):
            raise AttributeError("The service with the name '{0}' does not exist".format(name))
        self._services[name].start()