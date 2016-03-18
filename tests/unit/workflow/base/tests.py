
import unittest, colour_runner
from colour_runner.runner import ColourTextTestRunner, ColourTextTestResult

from ems.workflow.interfaces import WorkStep, WorkStepResult
from ems.workflow.base import Workflow
from ems.event.hook import TestListener

class WorkflowTest(unittest.TestCase):

    def test_next_without_startStep_raises_LookupError(self):
        workflow = self.newWorkflow()
        self.assertRaises(LookupError, workflow.next)

    def test_next_without_final_step_raises_LookupError(self):
        workflow = self.newWorkflow()
        startStep = WorkStep('start')
        workflow.startWith(startStep)
        self.assertRaises(LookupError, workflow.next)

    def test_next_raisesLookupError_if_no_transition_points_to_final_step(self):
        workflow = self.newWorkflow()
        startStep = WorkStep('start')
        success = startStep.addPossibleResult('success')
        endStep = WorkStep('end')
        endStep.final = True
        workflow.startWith(startStep)
        workflow.addTransition(success, startStep)

        self.assertRaises(LookupError, workflow.next)

    def test_next_returns_first_step_on_start_and_fires_events(self):
        workflow = self.newWorkflow()
        startStep = WorkStep('start')
        success = startStep.addPossibleResult('success')
        endStep = WorkStep('end')
        endStep.final = True
        workflow.startWith(startStep)
        workflow.addTransition(success, endStep)

        startingListener = TestListener()
        startedListener = TestListener()
        enteringListener = TestListener()
        enteredListener = TestListener()

        workflow.starting += startingListener
        workflow.started += startedListener
        workflow.entering += enteringListener
        workflow.entered += enteredListener

        step = workflow.next()

        self.assertIs(startStep.code, step.code)
        self.assertEqual(0, startingListener.callCount)
        self.assertEqual(0, startedListener.callCount)
        self.assertEqual(0, enteringListener.callCount)
        self.assertEqual(0, enteredListener.callCount)

        step.enter()

        self.assertEqual(1, startingListener.callCount)
        self.assertEqual(1, startedListener.callCount)
        self.assertEqual(1, enteringListener.callCount)
        self.assertIs(step, enteringListener.params[0])
        self.assertEqual(1, enteredListener.callCount)
        self.assertIs(step, enteredListener.params[0])

        self.assertTrue(workflow.isStarted())
        self.assertTrue(workflow.isActive())
        self.assertFalse(workflow.isFinished())

        step.enter()

        self.assertEqual(1, startingListener.callCount)
        self.assertEqual(1, startedListener.callCount)
        self.assertEqual(1, enteringListener.callCount)
        self.assertIs(step, enteringListener.params[0])
        self.assertEqual(1, enteredListener.callCount)
        self.assertIs(step, enteredListener.params[0])

        self.assertTrue(workflow.isStarted())
        self.assertTrue(workflow.isActive())
        self.assertFalse(workflow.isFinished())


    def test_next_returns_next_configured_step_and_fires_events(self):

        workflow = self.newWorkflow()
        startStep = WorkStep('start')
        success = startStep.addPossibleResult('success')
        endStep = WorkStep('end')
        endStep.final = True
        final = endStep.addPossibleResult('final')
        workflow.startWith(startStep)
        workflow.addTransition(success, endStep)

        startingListener = TestListener()
        startedListener = TestListener()
        enteringListener = TestListener()
        enteredListener = TestListener()
        leavingListener = TestListener()
        leavedListener = TestListener()
        finishingListener = TestListener()
        finishedListener = TestListener()

        workflow.starting += startingListener
        workflow.started += startedListener
        workflow.entering += enteringListener
        workflow.entered += enteredListener
        workflow.leaving += leavingListener
        workflow.leaved += leavedListener
        workflow.finishing += finishingListener
        workflow.finished += finishedListener

        step = workflow.next()

        self.assertIs(startStep.code, step.code)

        step.enter()

        testStep = workflow.next()

        self.assertIs(step, testStep)

        step.finish('success')

        self.assertEqual(1, leavingListener.callCount)
        self.assertEqual(1, leavedListener.callCount)
        self.assertIs(step, leavingListener.params[0])
        self.assertIs(step, leavedListener.params[0])

        self.assertEqual(1, enteringListener.callCount)
        self.assertIs(step, enteringListener.params[0])
        self.assertEqual(1, enteredListener.callCount)
        self.assertIs(step, enteredListener.params[0])

        lastStep = workflow.next()

        self.assertIs(endStep.code, lastStep.code)

        lastStep.enter()

        self.assertEqual(2, enteringListener.callCount)
        self.assertIs(lastStep, enteringListener.params[0])
        self.assertEqual(2, enteredListener.callCount)
        self.assertIs(lastStep, enteredListener.params[0])

        lastStep.finish('final')

        self.assertEqual(2, leavingListener.callCount)
        self.assertEqual(2, leavedListener.callCount)
        self.assertIs(lastStep, leavingListener.params[0])
        self.assertIs(lastStep, leavedListener.params[0])

        self.assertIs(lastStep, workflow.next())

        self.assertTrue(workflow.isFinished())
        self.assertEqual(1, finishingListener.callCount)
        self.assertEqual(1, finishedListener.callCount)

    def newWorkflow(self, *args, **kwargs):
        return Workflow(*args, **kwargs)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(WorkflowTest())
    return suite

if __name__ == '__main__':
    #suite = unittest.TestSuite()
    #suite.addTest(WorkflowTest())
    unittest.registerResult(ColourTextTestResult)
    unittest.main()
    #unittest.TextTestRunner().run(suite)