
from ems.event.hook import EventHook
from ems.qt import QtCore

QObject = QtCore.QObject

class SignalEventHookProxy(QObject):

    def __init__(self, qtSignal, parent=None):
        super(SignalEventHookProxy, self).__init__(parent)
        self.triggered = EventHook()
        self._qtSignal = qtSignal
        self._qtSignal.connect(self._listen)

    def _listen(self, *args):
        self.triggered.fire(*args)