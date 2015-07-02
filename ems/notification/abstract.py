
from abc import ABCMeta, abstractmethod


class FormNotifier(object):

    """
    A FormNotifier displays messages in a form. If this leads to write the
    messages into a session (http), to the view (templates) or a widget (pyqt)

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def showMessage(self, key, message, state=None):
        """
        Shows a message for key with state. An empty message will hide it
        :returns: Nothing
        """
        raise NotImplementedError()

    @abstractmethod
    def clearMessages(self):
        """
        Clear (hide) all messages
        :returns: Nothing
        """
        raise NotImplementedError()

    def showMessages(self, messages, state=None):
        """
        Show many messages at once
        """
        for fieldName in messages:
            self.showMessage(fieldName, messages[fieldName], state)