
from abc import ABCMeta, abstractmethod

from six import add_metaclass

@add_metaclass(ABCMeta)
class Workflow(object):

    def __init__(self):
        self.id = 0
        self.name = ''
        self.description = ''
        self.job = None
        self.active = True
        self.steps = []

@add_metaclass(ABCMeta)
class WorkStep(object):

    def __init__(self):
        self.code = ''
        self.name = ''
        self.description = ''
        self.due_days = 0
        self.job = None

@add_metaclass(ABCMeta)
class WorkflowDirector(object):

    @abstractmethod
    def workflow(self, order):
        pass

    @abstractmethod
    def next(self, order):
        pass

    @abstractmethod
    def hasNext(self, order):
        pass

    @abstractmethod
    def previous(self, order):
        pass

    @abstractmethod
    def hasPrevious(self, order):
        pass

    @abstractmethod
    def current(self, order):
        pass

    @abstractmethod
    def complete(self, order, workStep):
        pass

    @abstractmethod
    def postpone(self, order, workStep):
        pass

    @abstractmethod
    def isCompleted(self, order, workStep):
        pass

    @abstractmethod
    def isPostponed(self, order, workStep):
        pass