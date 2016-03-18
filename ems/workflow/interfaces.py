
from abc import ABCMeta, abstractmethod

from six import add_metaclass

from ems.event.hook import EventHookProperty, EventHook

@add_metaclass(ABCMeta)
class Identifiable(object):
    def __init__(self, id_=None):
        self.id = id_

class Orderer(Identifiable):
    """
    An Orderer is the causer of an order
    """
    pass

class OrderCategory(Identifiable):
    """
    An OrderCategory is the category of an order
    """

class Order(Identifiable):
    """
    An Order is the "action" which triggers the start of a workflow
    """
    def __init__(self, id_=None, orderer=None, category=None):
        super().__init__(id_)
        self.orderer = orderer
        self.category = category

class Job(Identifiable):
    """
    A job is a classification of actions a user is responsible for
    """
    pass

@add_metaclass(ABCMeta)
class HumanReadable(object):
    pass

class WorkStepResult(object):
    """
    A WorkStepResult is the result of a workstep. On basis of the WorkStepResult
    the next WorkStep will be deceided
    """
    def __init__(self, code='', name='', description='', workStep=None, params=None):
        self.code = code
        self.name = name
        self.description = description
        self.workStep = workStep
        self.params = {} if params is None else params

class WorkStep(object):
    """
    A Workstep is one step, usually one unit of an user interface like one form
    with one ore more possible results.
    The Workstep has to deliver all possible results via results()
    No other result can occur during processing this workstep.
    You can get the current workstep by its workflow via:
    workflow.next()
    Than workstep.entering() is triggered and this workflow will be returned
    by next() until finished(WorkStepResult) of this workstep is triggered.
    
    """

    def __init__(self, code='', name='', description='', job=None, dueDays=0):
        self.code = code
        self.name = name
        self.description = description
        self.dueDays = 0
        self.job = job
        self.parent = None
        self.children = []
        self._result = None
        self._isEntered = False
        self._isFinished = False
        self.possibleResults = []
        self.entering = EventHook()
        self.entered = EventHook()
        self.finishing = EventHook()
        self.finished = EventHook()
        self.leaving = EventHook()
        self.returning = EventHook()
        self._isFirstStep = False
        self._isFinalStep= False

    def isGroup(self):
        pass

    def isParallel(self):
        pass

    def enter(self):
        if self._isEntered:
            return
        self._isFinished = False
        self._isEntered = False
        self.entering.fire()
        self._isEntered = True
        self.entered.fire()

    def finish(self, resultCode, params=None):
        if self._isFinished:
            return
        result = self.createResultFor(resultCode)
        print(self.code, 'finishing', resultCode)
        self.finishing.fire(result)
        self._isFinished = True
        self._isEntered = False
        self._result = result
        self.finished.fire(result)

    def isEntered(self):
        return self._isEntered

    def isFinished(self):
        return self._isFinished

    def isActive(self):
        return self.isEntered() and not self.isFinished()

    @property
    def result(self):
        return self._result

    def isFirstStep(self):
        return self._isFirstStep

    def setIsFirstStep(self, isFirst):
        self._isFirstStep = isFirst

    first = property(isFirstStep, setIsFirstStep)

    def isFinalStep(self):
        return self._isFinalStep

    def setIsFinalStep(self, isFinal):
        self._isFinalStep = isFinal

    final = property(isFinalStep, setIsFinalStep)

    def addPossibleResult(self, result):
        result = result if isinstance(result, WorkStepResult) else self.newResult(code=result)
        result.workflow = self
        self.possibleResults.append(result)
        return result

    def possibleResult(self, code):
        for result in self.possibleResults:
            if result.code == code:
                return result
        raise KeyError('Result with code {} not found'.format(code))

    def createResultFor(self, code):
        return self.possibleResult(code)

    def newResult(self, *args, **kwargs):
        return WorkStepResult(*args, **kwargs)

    def notifyLeave(self):
        '''
        This method is called before the last WorkStep in history is selected.
        User presses back button, than this method is called, than the last
        workstep will be the current
        '''
        self.leaving.fire()

    def notifyReturn(self):
        '''
        This method is called after switching back to the last WorkStep. The
        method is called on the WorkStep which will then be the current
        '''
        self._isFinished = False
        self._result = None
        self.returning.fire()

    def toOccurrence(self):
        '''
        This method copies the workflow for each occurence inside the history
        The original workstep never gets touched. It works as a template for
        the real occuring worksteps
        '''
        copy = self.__class__(self.code, self.name, self.description, self.job, self.dueDays)
        for result in self.possibleResults:
            copy.possibleResults.append(result)

        copy.first = self.first
        copy.final = self.final
        return copy


class WorkStepTransition(object):
    """
    A WorkStepTransition represents the transition between 2 WorkSteps
    It allows to ask for the connections of the first step
    """
    def __init__(self, lastResult, nextStep):
        self.lastResult = lastResult
        self.nextStep = nextStep

@add_metaclass(ABCMeta)
class Workflow(object):
    """
    A Workflow manages all steps. It is not a value object like WorkStep,
    WorkStepTransition, WorkStepResult and so forth.
    It does the actual processing of WorkSteps.

    It is configured via addTransition() and startWith().
    The initial step is added via startWith(workStep)
    Than all following worksteps are configured via
    addTransition(stepResult, nextWorkStep)

    After configuring the workflow it returns the initial step on next()
    If you finish the returned workstep its finished event is fired via its
    hook. The Workflow subscribes to this event and transits to the next workstep

    So the complete flow is:

    bookInvoice = WorkStep()
    booked = WorkStepResult(code='accounting.booked')
    furtherInquiry = WorkStepResult(code='accounting.further-inquiry')
    bookInvoice.addPossibleResult(booked, furtherInquiry)
    bookInvoice.first = True

    showBookingSummary = WorkStep()
    showBookingSummary.final = True

    handleFurtherInquiries = WorkStep()
    askForHelp = WorkStepResult(code='accounting.ask-for-help')
    infoRetrieved = WorkStepResult(code='accounting.info-retrieved')
    handleFurtherInquiries.addPossibleResult(askForHelp, infoRetrieved)

    workflow = WorkFlow()
    workflow.startWith(bookInvoice)
    workflow.addTransition(bookInvoice, showBookingSummary)
    workflow.addTransition(furtherInquiry, handleFurtherInquiries)
    workflow.addTransition(infoRetrieved, bookInvoice)
    workflow.addTransition(askForHelp, handleFurtherInquiries)

    # Until here the workflow is configured

    step = workflow.next() # returns bookInvoice
    step.finish('accounting.further-inquiry')

    step = workflow.next() # returns handleFurtherInquiries
    step.finish('accounting.ask-for-help')

    step = workflow.next() # returns handleFurtherInquiries
    step.finish('accounting.info-retrieved')

    step = workflow.next() # returns bookInvoice
    step.finish('accounting.booked')

    workflow.next() # returns showBookingSummary

    """
    def __init__(self, code='', id_=None, name='', description=''):
        self.id = id_
        self.code = code
        self.name = ''
        self.description = ''
        self.active = True
        self.steps = []
        self.order = None

        self.starting = EventHook()
        self.started = EventHook()

        self.entering = EventHook()
        self.entered = EventHook()
        self.completing = EventHook()
        self.completed = EventHook()
        self.returned = EventHook()

        self.finishing = EventHook()
        self.finished = EventHook()
        self.transitioning = EventHook()

    @abstractmethod
    def next(self):
        '''
        Returns the next WorkStep. If it is finished it returns the final step
        If it is not started it returns the first step
        '''
        pass

    @abstractmethod
    def back(self):
        '''
        Cancels the current workstep and return to the last in history. Returns
        true if it was successful, false if not. You cant back from a startStep
        '''

    @abstractmethod
    def startWith(self, workStep):
        '''
        Set the first workstep of this workflow
        '''
        pass

    @abstractmethod
    def addTransition(self, previousStepResult, nextWorkStep):
        '''
        Set the following step based on previousStepResult
        '''
        pass

    @abstractmethod
    def transition(self, stepResult):
        '''
        Return the transition which occurs if stepResult is occuring
        '''
        pass

    @abstractmethod
    def isStarted(self):
        '''
        Return if this workflow has been started
        '''
        pass

    @abstractmethod
    def isFinished(self):
        '''
        Return if this workflow has been finished
        '''
        pass

    def isActive(self):
        '''
        Return if the workflow is currently running
        '''
        return self.isStarted() and not self.isFinished()


@add_metaclass(ABCMeta)
class WorkflowManager(object):
    '''
    The WorkflowManager returns workflows for orders. If order x is passed, a
    matching workflow will be returned.
    If worksteps have to been done in parallel, this system needs to be
    extended by ParallelWorkStep objects and not by returning multiple
    workflows.

    The manager can also persist the state of a workflow. If you ask for a
    workflow for an order the manager has to search for a saved workflow and
    return the saved one. If no saved workflow is found, a new will be returned
    '''
    @abstractmethod
    def workflow(self, order):
        pass

    @abstractmethod
    def saveState(self, workflow):
        pass

    @abstractmethod
    def clearState(self, workflow):
        pass

    @abstractmethod
    def hasState(self, workflow):
        pass