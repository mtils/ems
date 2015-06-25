

from PyQt4.QtCore import QObject, pyqtSignal

from ems.qt4.gui.widgets.balloontip import BalloonTip



class InputErrorMessenger(QObject):

    def __init__(self, parent=None):
        super(InputErrorMessenger, self).__init__(parent)
        self._widgetMap = {}
        self._balloons = {}
        self._defaultState = BalloonTip.ERROR


    def map(self, fieldName, widget):
        self._widgetMap[fieldName] = widget
        self._balloons[fieldName] = BalloonTip(widget)

    def mapAll(self, widgetDict):
        for fieldName in widgetDict:
            self.map(fieldName, widgetDict[fieldName])


    def showMessage(self, fieldName, message, state=None):

        state = self._defaultState if state is None else state

        if not fieldName in self._balloons:
            return

        self._balloons[fieldName].setState(state)
        self._balloons[fieldName].setMessage(message)
        self._balloons[fieldName].show()

    def showMessages(self, messages, state=None):

        state = self._defaultState if state is None else state

        for fieldName in messages:
            self.showMessage(fieldName, messages[fieldName], state)