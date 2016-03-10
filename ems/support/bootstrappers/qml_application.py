
import os.path

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtQml import QQmlComponent, qmlRegisterSingletonType
from PyQt5.QtQml import qmlRegisterType
from PyQt5.QtQuick import QQuickView

from ems.app import Bootstrapper
from ems.qt.qml_dispatcher import QmlDispatcher, QmlFileLoader
from ems.qt5.qml_dispatcher import ComponentCreator
from ems.qt5.qml_factory import Factory
from ems.qt5.util import qmlImportPath
from ems.qt5.itemmodel.custom_filtermodel import SortFilterProxyModel
from ems.qt5.itemmodel.sequencecolumn_model import SequenceColumnModel
from ems.qt5.itemmodel.current_row_proxymodel import CurrentRowProxyModel


class QmlApplicationBootstrapper(Bootstrapper):

    def __init__(self):
        self.app = None
        self._win = None
        self._features = None
        self._registry = None

    def bootstrap(self, app):

        self.app = app

        self.qmlPath = self.qmlFilePath()

        self.app.booted += self.createHiddenMainWindow

        app['events'].listen('auth.loggedIn', self.showMainWindow)
        app['events'].listen('auth.loggedOut', self.hideMainWindow)

    def createHiddenMainWindow(self, app):

        self.win = QQuickView()

        self.win.setResizeMode(QQuickView.SizeRootObjectToView)
        self.addQmlImportPaths(self.win.engine())

        qmlapp = Factory(self.win.engine(), None)
        app.shareInstance('qmlapp', qmlapp)

        qmlRegisterSingletonType(Factory, 'org.ems', 1, 0, 'QmlFactory', Factory.new)
        qmlRegisterType(SortFilterProxyModel, 'org.ems', 1, 0, 'FilterModel')
        qmlRegisterType(SequenceColumnModel, 'org.ems', 1, 0, 'SequenceColumnModel')
        qmlRegisterType(CurrentRowProxyModel, 'org.ems', 1, 0, 'CurrentRowModel')

        self.win.engine().rootContext().setContextProperty("qmlApp", qmlapp)

        qmlFileUrl = self.mainQmlFileUrl()

        if qmlFileUrl:
            self.win.setSource(qmlFileUrl)
        else:
            self.app('events').listen("qml.apply-url", self.win.setSource)

        self.win.resize(1076,700)
        self.win.hide()

        app['events'].fire('gui.ready')

    def showMainWindow(self, *args):
        self.win.show()

    def hideMainWindow(self):
        self.win.hide()

    def addQmlImportPaths(self, engine):
        engine.addImportPath(qmlImportPath())

    def qmlFilePath(self):
        return os.path.join(self.app.path,'resources','qml')

    def mainQmlFileUrl(self):
        return None
        return QUrl.fromLocalFile(os.path.join(self.qmlPath, 'desktop.qml'))