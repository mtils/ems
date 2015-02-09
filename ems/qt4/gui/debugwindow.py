import sys
from PyQt4.QtCore import QString, qInstallMsgHandler
from PyQt4.QtGui import QTextEdit, QTextCursor, QColor

class IORedirector(object):

    debugWindow = None
    alternateOut = None
    color = QColor(0,0,0)

    def write(self, message):
        previousColor = self.debugWindow.textColor()
        self.debugWindow.setTextColor(self.color)
        self.debugWindow.insertPlainText(QString.fromUtf8(message))
        self.debugWindow.setTextColor(previousColor)
        self.debugWindow.verticalScrollBar().setValue(self.debugWindow.verticalScrollBar().maximum())
        #if self.alternateOut:
            #self.alternateOut.write(message)
            
class QtIORedirector(IORedirector):
    def write(self, msgType, message):
        IORedirector.write(self, message)

class DebugWindow(QTextEdit):

    stdErrorWriter = None
    stdOutWriter = None
    loggingWriter = None
    qtDebugMessageWriter = None
    defaultColor = QColor(0,0,0)

    def __init__(self, alternateOut=None, parent=None):
        QTextEdit.__init__(self, parent)
        self.alternateOut = alternateOut
        self.setReadOnly(True)

    def enableStdOutRedirection(self, color=None):
        if color is None:
            color = QColor(0,0,0)
        self.stdOutWriter = IORedirector()
        self.stdOutWriter.color = color
        self.stdOutWriter.debugWindow = self
        self.stdOutWriter.alternateOut = sys.stdout
        
        sys.stdout = self.stdOutWriter
        
    
    def enableStdErrRedirection(self, color=None):
        if color is None:
            color = QColor(255,0,0)
        self.stdErrorWriter = IORedirector()
        self.stdErrorWriter.color = color
        self.stdErrorWriter.debugWindow = self
        self.stdErrorWriter.alternateOut = sys.stderr
        sys.stderr = self.stdErrorWriter
    
    def enableQtMsgRedirection(self, color=None):
        if color is None:
            color = QColor(0,255,0)
        self.qtMessageWriter = QtIORedirector()
        self.qtMessageWriter.color = color
        self.qtMessageWriter.debugWindow = self
        #self.stdErrorWriter.alternateOut = sys.__stderr__
        
        qInstallMsgHandler(self.qtMessageWriter.write)