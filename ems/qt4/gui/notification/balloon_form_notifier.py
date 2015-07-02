

from PyQt4.QtCore import QObject, pyqtSignal

from ems.notification.abstract import FormNotifier
from ems.qt4.gui.widgets.balloontip import BalloonTip
from ems import qt4
from ems.qt4.util import variant_to_pyobject as py



class BalloonFormNotifier(FormNotifier):

    def __init__(self):
        self._widgetMap = {}
        self._balloons = {}
        self._defaultState = BalloonTip.ERROR
        self._model = None
        self._currentModelRow = 0


    def map(self, key, widget):
        self._widgetMap[key] = widget
        self._balloons[key] = BalloonTip(widget)
        self._balloons[key].setArrowAtLeft(True)
        self._balloons[key].setArrowAtTop(False)

    def mapAll(self, widgetDict):
        for fieldName in widgetDict:
            self.map(fieldName, widgetDict[fieldName])


    def showMessage(self, key, message, state=None):

        state = self._defaultState if state is None else state

        if not key in self._balloons:
            return

        if not len(message):
            self._balloons[key].setMessage(message)
            self._balloons[key].hide()
            return

        self._balloons[key].setState(state)
        self._balloons[key].setMessage(message)
        self._balloons[key].show()

    def clearMessages(self):
        for key in self._balloons:
            self._balloons[key].setMessage('')
            self._balloons[key].hide()

    def getModel(self):
        return self._model

    def setModel(self, model):
        self._connectToModel(model)
        self._model = model
        self._updateMessagesFromModel()

    model = property(getModel, setModel)

    def getCurrentModelRow(self):
        return self._currentModelRow

    def setCurrentModelRow(self, row):
        self._currentModelRow = row
        self._updateMessagesFromModel()

    currentModelRow = property(getCurrentModelRow, setCurrentModelRow)

    def _connectToModel(self, model):
        model.messageChanged.connect(self._onModelMessageChanged)
        model.messagesCleared.connect(self._onModelMessageCleared)

    def _onModelMessageChanged(self, row, column, message):

        if row != self._currentModelRow:
            return

        keyName = py(self._model.index(row, column).data(qt4.ColumnNameRole))

        self.showMessage(keyName, message)

    def _onModelMessageCleared(self, row):

        if row != self._currentModelRow:
            return

        self.clearMessages()

    def _updateMessagesFromModel(self):

        self.clearMessages()
        row = self._currentModelRow

        for column in range(self._model.columnCount()):
            keyName = py(self._model.index(row, column).data(qt4.ColumnNameRole))
            self.showMessage(keyName, self._model.columnMessage(row, column))