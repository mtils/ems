
import os.path

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtQml import QQmlComponent, qmlRegisterSingletonType
from PyQt5.QtQml import qmlRegisterType
from PyQt5.QtQuick import QQuickView

from ems.app import Bootstrapper
from ems.support.bootstrappers.qapplication import QApplicationBootstrapper
from ems.qt.qml_dispatcher import QmlDispatcher, QmlFileLoader
from ems.qt5.qml_dispatcher import ComponentCreator
from ems.qt5.qml_factory import Factory
from ems.qt5.itemmodel.custom_filtermodel import SortFilterProxyModel
from ems.qt5.itemmodel.sequencecolumn_model import SequenceColumnModel
from ems.qt5.itemmodel.current_row_proxymodel import CurrentRowProxyModel


class QmlApplicationBootstrapper(QApplicationBootstrapper):

    def setupPaths(self):
        self.qmlPath = self.qmlFilePath()

    def createHiddenMainWindow(self, app):

        self.win = win = QQuickView()
        win.statusChanged.connect(self._onQQuickViewStatusChanged)

        win.setResizeMode(QQuickView.SizeRootObjectToView)
        self.addQmlImportPaths(win.engine())

        qmlapp = Factory(win.engine(), None)
        app.shareInstance('qmlapp', qmlapp)

        qmlRegisterSingletonType(Factory, 'org.ems', 1, 0, 'QmlFactory', Factory.new)
        qmlRegisterType(SortFilterProxyModel, 'org.ems', 1, 0, 'FilterModel')
        qmlRegisterType(SequenceColumnModel, 'org.ems', 1, 0, 'SequenceColumnModel')
        qmlRegisterType(CurrentRowProxyModel, 'org.ems', 1, 0, 'CurrentRowModel')

        win.engine().rootContext().setContextProperty("qmlApp", qmlapp)

        qmlFileUrl = self.mainQmlFileUrl()

        if qmlFileUrl:
            win.setSource(qmlFileUrl)
        else:
            self.app('events').listen("qml.apply-url", win.setSource)

        win.resize(1076,700)
        win.hide()

        return win

    def addQmlImportPaths(self, engine):
        engine.addImportPath(self._qmlImportPath())

    def qmlFilePath(self):
        return os.path.join(self.app.path,'resources','qml')

    def mainQmlFileUrl(self):
        return None

    def _onQQuickViewStatusChanged(self, status):
        if status != QQuickView.Ready:
            return

        root = self.win.rootObject()
        try:
            root.itemCreated.connect(self._forwardItemsToEvents)
        except AttributeError:
            return

    def _forwardItemsToEvents(self, item):
        self.app['events'].fire('qml.item-created', item)

    def _qmlImportPath(self, compiled=False):
        if not compiled:
            return os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),'..','..','qt5','assets','qml'
                )
            )