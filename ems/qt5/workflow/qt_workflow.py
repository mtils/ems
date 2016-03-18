
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty

from ems.workflow.base import Workflow

class Proxy(QObject):

    def __init__(self, source):
        super().__init__()
        self._source = source

    def getCode(self):
        return self._source.code

    code = pyqtProperty('QString', getCode)

    def getName(self):
        return self._source.name

    name = pyqtProperty('QString', getName)

    def getDescription(self):
        return self._source.description

    description = pyqtProperty('QString', getDescription)

class ProxyWorkStepResult(Proxy):

    def __init__(self, source):
        super().__init__(source)
        self._workStep = None

    def getWorkStep(self):
        if self._workStep:
            return self._workStep
        self._workStep = ProxyWorkStep(self._source.workStep)
        return self._workStep

    def _setWorkStep(self, workStep):
        self._workStep = workStep

    def getParams(self):
        return self._source.params

    params = pyqtProperty('QVariantMap', getParams)

class ProxyWorkStep(Proxy):

    entering = pyqtSignal()
    entered = pyqtSignal()
    finishing = pyqtSignal(ProxyWorkStepResult)
    finished = pyqtSignal(ProxyWorkStepResult)
    leaving = pyqtSignal()

    def __init__(self, source):
        super().__init__(source)
        source.entering += self.entering.emit
        source.entered += self.entered.emit
        source.finishing += self._onSourceFinishing
        source.finished += self._onSourceFinished
        source.leaving += self.leaving.emit

    def getDueDays(self):
        return self._source.dueDays

    dueDays = pyqtProperty(int, getDueDays)

    def getParent(self):
        parent = self._source.parent
        if parent:
            return ProxyWorkStep(parent)

    @pyqtSlot()
    def enter(self):
        self._source.enter()

    @pyqtSlot(str)
    @pyqtSlot(str, 'QVariantMap')
    def finish(self, resultCode, params=None):
        self._source.finish(resultCode, params)

    def _onSourceFinishing(self, result):
        qResult = ProxyWorkStepResult(result)
        qResult._setWorkStep(self)
        self.finishing.emit(qResult)

    def _onSourceFinished(self, result):
        qResult = ProxyWorkStepResult(result)
        qResult._setWorkStep(self)
        self.finished.emit(qResult)

ProxyWorkStep.parent = pyqtProperty(ProxyWorkStep, ProxyWorkStep.getParent)

ProxyWorkStepResult.workStep = pyqtProperty(ProxyWorkStep, ProxyWorkStepResult.getWorkStep)

class ProxyWorkflow(Proxy):

    starting = pyqtSignal()
    started = pyqtSignal()
    finishing = pyqtSignal()
    finished = pyqtSignal()
    returned = pyqtSignal()

    entering = pyqtSignal(ProxyWorkStep)
    entered = pyqtSignal(ProxyWorkStep)
    completing = pyqtSignal(ProxyWorkStep)
    completed = pyqtSignal(ProxyWorkStep)

    def __init__(self, source):
        super().__init__(source)
        source.starting += self.starting.emit
        source.started += self.started.emit
        source.finishing += self.finishing.emit
        source.finished += self.finished.emit
        source.entering += self._onSourceEntering
        source.entered += self._onSourceEntered
        source.completing += self._onSourceLeaving
        source.completed += self._onSourceLeaved
        source.returned += self.returned.emit

    @pyqtSlot(result=ProxyWorkStep)
    def next(self):
        step = self._source.next()
        if step:
            return ProxyWorkStep(step)

    @pyqtSlot(result=bool)
    def back(self):
        return self._source.back()

    @pyqtSlot(result=bool)
    def isStarted(self):
        return self._source.isStarted()

    @pyqtSlot(result=bool)
    def isFinished(self):
        return self._source.isFinished()

    @pyqtSlot(result=bool)
    def isActive(self):
        return self._source.isActive()

    def _onSourceEntering(self, step):
        self.entering.emit(ProxyWorkStep(step))

    def _onSourceEntered(self, step):
        self.entered.emit(ProxyWorkStep(step))

    def _onSourceLeaving(self, step):
        self.completing.emit(ProxyWorkStep(step))

    def _onSourceLeaved(self, step):
        self.completed.emit(ProxyWorkStep(step))


class ProxyWorkflowManager(QObject):

    def __init__(self, source):
        super().__init__()
        self._source = source

    def workflow(self, order):
        workflow = self._source.workflow(order)
        return ProxyWorkflow(workflow)