
from ems.workflow.interfaces import Orderer, OrderCategory, Order, Job
from ems.workflow.interfaces import WorkStepResult, WorkStep
from ems.workflow.interfaces import WorkStepTransition
from ems.workflow.interfaces import Workflow as AbstractWorkflow
from ems.workflow.interfaces import WorkflowManager as AbstractWorkflowManager

class Workflow(AbstractWorkflow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._startStep = None
        self._started = False
        self._transitionsByCode = {}
        self._history = []

    def next(self):

        if not len(self._history):
            self._checkIntegrity()
            currentStep = self._createOccurrence(self._startStep)
            currentStep.entering += self._onFirstStepEntering
            currentStep.entered += self._onFirstStepEntered
            self._pushStep(currentStep)
            return currentStep

        currentStep = self._currentStep

        if not currentStep.isFinished() or currentStep.isFinalStep():
            return currentStep

        # not isFinalStep() and isFinished()
        result = currentStep.result
        currentStep = self._createOccurrence(self._findNextStep(result))
        print("created fresh step", currentStep.code)

        self._pushStep(currentStep)

        return currentStep

    def back(self):
        if len(self._history) < 2:
            return False
        currentStep = self._currentStep
        currentStep.notifyLeave()
        self._popStep()
        self._currentStep.notifyReturn()
        self.returned.fire()
        print("returning to", self._currentStep, self._currentStep.code)
        return True

    def startWith(self, workStep):
        self._startStep = workStep
        return self

    def addTransition(self, previousStepResult, nextWorkStep):
        self._transitionsByCode[previousStepResult.code] = WorkStepTransition(previousStepResult, nextWorkStep)
        return self

    def transition(self, stepResult):
        code = stepResult if not isinstance(stepResult, WorkStepResult) else stepResult.code
        return self._transitionsByCode[code]

    def isStarted(self):
        return self._started

    def isFinished(self):
        step = self.next()
        return step.isFinalStep() and step.isFinished()

    def restore(self, state):
        '''
        Restores the current state by a WorkflowState object
        '''
        self._started = True
        for transition in self._transitionsByCode.values():
            if transition.nextStep.code != code:
                continue
            self._currentStep = self._createOccurrence(transition.nextStep)


    @property
    def _currentStep(self):
        try:
            return self._history[-1]
        except IndexError:
            return None

    def _pushStep(self, step):
        self._history.append(step)
        return step

    def _popStep(self):
        step = self._history.pop()
        return step

    def _createOccurrence(self, step):
        #self._bootStep(step)
        #return step
        occurrence = step.toOccurrence()
        self._bootStep(occurrence)
        return occurrence

    def _findNextStep(self, lastStepResult):
        transition = self.transition(lastStepResult)
        return transition.nextStep


    def _bootStep(self, workStep):
        workStep.entering += self._onCurrentStepEntering
        workStep.entered += self._onCurrentStepEntered
        workStep.finishing += self._onCurrentStepFinishing
        workStep.finished += self._onCurrentStepFinished

    def _onFirstStepEntering(self):
        if self._started:
            return
        self.starting.fire()

    def _onFirstStepEntered(self):
        if self._started:
            return
        self._started = True
        self.started.fire()

    def _onCurrentStepEntering(self):
        self.entering.fire(self._currentStep)

    def _onCurrentStepEntered(self):
        self.entered.fire(self._currentStep)

    def _onCurrentStepFinishing(self, result):
        self.completing.fire(self._currentStep)
        if self._currentStep.isFinalStep():
            self.finishing.fire()

    def _onCurrentStepFinished(self, result):
        self.completed.fire(self._currentStep)
        if self._currentStep.isFinalStep():
            self.finished.fire()

    def _checkIntegrity(self):

        if not self._startStep:
            raise LookupError('No startstep assigned')

        for code, transition in self._transitionsByCode.items():
            if transition.nextStep.isFinalStep():
                return

        raise LookupError('No transitions point to a finalstep')

class WorkflowProvider(object):
    '''
    The WorkflowProvider deceides which workflow has to be created for order
    '''
    def new(self, order):
        return Workflow()

class WorkflowState(object):
    '''
    A WorkflowState represents the state of a workflow. The state contains the
    workstep code which was the current code the user worked on and arbitrary
    params of the workstep
    '''
    def __init__(self):
        self.orderId = 0
        self.workflowId = ''
        self.stepCode = ''
        self.params = ''

class WorkflowManager(AbstractWorkflowManager):

    def __init__(self, provider, repository):
        self._provider = provider
        self._repository = repository

    def workflow(self, order):
        workflow = self._provider.new(order)
        existingWorkflowState = self._repository.getState(workflow)
        if existingWorkflowState:
            workflow.restore(existingWorkflowState)
        return workflow

    def saveState(self, workflow):
        state = self._repository.new()
        state.workflowId = workflow.id
        state.orderId = workflow.order.id
        step = workflow.next()
        state.stepCode = step.code
        self._repository.saveState(state)

    def clearState(self, workflow):
        existingWorkflowState = self._repository.getState(workflow)
        self._repository.delete(existingWorkflowState)

    def hasState(self, workflow):
        existingWorkflowState = self._repository.getState(workflow)
        return bool(existingWorkflowState)

if __name__ == '__main__':
    workflow = Workflow()
    step = workflow.next()
    print(workflow)